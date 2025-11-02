import json
import os
from typing import Any, Dict

import requests
import streamlit as st
from load_dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Supervisor AI Assistant", page_icon="🤖")


def ensure_api_key(api_key: str) -> None:
    """Persist the provided API key in the environment for downstream libraries."""
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key


def render_agent_caption(metadata: Dict[str, Any]) -> None:
    """Display the agent that handled the response."""
    if not metadata:
        return
    agent = metadata.get("selected_agent")
    reason = metadata.get("reason_selection")
    caption_parts = []
    if agent:
        caption_parts.append(f"routed to `{agent}`")
    if reason:
        caption_parts.append(reason)
    if caption_parts:
        st.caption(" • ".join(caption_parts))


def render_message(role: str, content: str, metadata: Dict[str, Any] | None = None) -> None:
    with st.chat_message(role):
        st.markdown(content)
        if role == "assistant":
            render_agent_caption(metadata or {})
            raw = (metadata or {}).get("raw_response")
            if raw:
                with st.expander("Raw response", expanded=False):
                    st.json(raw)


if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Settings")
    api_base = st.text_input("API base URL", value=os.getenv("API_BASE_URL", "http://localhost:8000"))
    provided_key = st.text_input(
        "OpenAI API Key",
        value=os.getenv("OPENAI_API_KEY", ""),
        type="password",
        help="Used by the backend for embeddings and LLM calls.",
    )
    ensure_api_key(provided_key)

    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()

st.title("Supervisor AI Assistant")
st.write("Chat with the supervisor router to ask questions or summarize incidents.")

for message in st.session_state.messages:
    render_message(
        message["role"],
        message["content"],
        message.get("metadata"),
    )

if prompt := st.chat_input("Send a message"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_message("user", prompt)

    try:
        response = requests.post(
            f"{api_base.rstrip('/')}/query",
            json={"query": prompt},
            timeout=120,
        )
        response.raise_for_status()
        payload: Dict[str, Any] = response.json()
    except requests.RequestException as exc:
        error_message = f"Request failed: {exc}"
        st.session_state.messages.append({"role": "assistant", "content": error_message})
        render_message("assistant", f":red[Error] {error_message}")
    else:
        structured = payload.get("structured_response")
        if isinstance(structured, dict):
            answer_text = f"```json\n{json.dumps(structured, indent=2, ensure_ascii=False)}\n```"
            metadata = {
                "selected_agent": structured.get("selected_agent"),
                "reason_selection": structured.get("reason_selection"),
            }
        else:
            final_answer: Any = payload.get("final_answer")
            if isinstance(final_answer, dict):
                answer_text = f"```json\n{json.dumps(final_answer, indent=2, ensure_ascii=False)}\n```"
            elif final_answer is not None:
                answer_text = str(final_answer)
            else:
                messages = payload.get("messages") or []
                last_message = messages[-1] if messages else {}
                if isinstance(last_message, dict):
                    answer_text = str(last_message.get("content", last_message))
                else:
                    answer_text = str(last_message) if last_message else "No response."
            metadata = {
                "selected_agent": payload.get("selected_agent"),
                "reason_selection": payload.get("reason_selection"),
            }

        metadata = {k: v for k, v in metadata.items() if v}
        metadata["raw_response"] = payload

        assistant_message = {
            "role": "assistant",
            "content": answer_text,
            "metadata": metadata,
        }
        st.session_state.messages.append(assistant_message)
        render_message("assistant", answer_text, assistant_message["metadata"])
