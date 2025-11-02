# framework imports
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage

# module imports
from .state import ReportedIssueOut, AffectedComponentsOut, SeverityOut, State
from .prompt import SYSTEM_PROMPT_REPORTED_ISSUE, SYSTEM_PROMPT_AFFECTED_COMPONENTS, SYSTEM_PROMPT_SEVERITY

# system imports
import os
import getpass
# from dotenv import load_dotenv
# load_dotenv()

def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("OPENAI_API_KEY")


# Import model
llm = init_chat_model(model="gpt-4o")

# Nodes

def llm_reported_issue(state: State):
    """call to generate reported issue"""
    msgs = [
        SystemMessage(content=SYSTEM_PROMPT_REPORTED_ISSUE),
        HumanMessage(content=state["issue_text"])
    ]
    response: ReportedIssueOut = llm.with_structured_output(ReportedIssueOut).invoke(msgs)
    print(response)
    return {"reported_issue": response.reported_issue.strip()}


def llm_affected_components(state: State):
    """call to generate affected components"""
    msgs = [
        SystemMessage(content=SYSTEM_PROMPT_AFFECTED_COMPONENTS),
        HumanMessage(content=state["issue_text"])
    ]
    response: AffectedComponentsOut = llm.with_structured_output(AffectedComponentsOut).invoke(msgs)
    return {"affected_components": response.affected_components}

def llm_severity(state: State):
    """call to generate severity"""
    msgs = [
        SystemMessage(content=SYSTEM_PROMPT_SEVERITY),
        HumanMessage(content=state["issue_text"])
    ]
    response: SeverityOut = llm.with_structured_output(SeverityOut).invoke(msgs)
    return {"severity": response.severity}


