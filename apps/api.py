import logging
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field
from dotenv import load_dotenv
load_dotenv()

import sys, os
parent_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from agents import AIAssistant



logger = logging.getLogger(__name__)

app = FastAPI(
    title="Supervisor AI Assistant API",
    description="FastAPI surface for routing user queries through the LangGraph supervisor agent.",
)


class QueryRequest(BaseModel):
    query: str = Field(..., description="End-user question or issue text.")


def _serialize(value: Any) -> Any:
    """Recursively convert agent outputs into JSON-serializable structures."""
    if isinstance(value, BaseMessage):
        return _serialize(value.model_dump())
    if hasattr(value, "model_dump"):
        return _serialize(value.model_dump())
    if hasattr(value, "dict"):
        return _serialize(value.dict())
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if isinstance(value, tuple):
        return [_serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    return value


@app.get("/health")
async def health() -> Dict[str, str]:
    """Simple readiness probe."""
    return {"status": "ok"}


@app.post("/query")
async def handle_query(payload: QueryRequest) -> JSONResponse:
    """Route a user query through the supervisor agent and return its response."""
    try:
        result = AIAssistant.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": payload.query.strip(),
                    }
                ]
            }
        )
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Failed to invoke supervisor agent")
        raise HTTPException(status_code=500, detail="Agent invocation failed") from exc

    serialized = _serialize(result)
    return JSONResponse(content=jsonable_encoder(serialized))
