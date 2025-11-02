from langchain.tools import tool
from .prompt import INTERNAL_QA_TOOL_DESC, ISSUE_SUMMARY_TOOL_DESC 
from agents import InternalQAGraphAgent, IssueSummaryGraphAgent

## create tool wrappers node for sub-agents 
@tool(
    "InternalQAGraphAgentTool",
    description=INTERNAL_QA_TOOL_DESC
)
def InternalQAGraphAgentTool(query: str):
    result = InternalQAGraphAgent.invoke({
        "messages": [{"role": "user", "content": query}]
    })
    return result["messages"][-1].content
    # return str(result)

@tool(
    "IssueSummaryGraphAgentTool",
    description=ISSUE_SUMMARY_TOOL_DESC
)
def IssueSummaryGraphAgentTool(query: str):
    result = IssueSummaryGraphAgent.invoke({
        "issue_text": query
    })
    return result