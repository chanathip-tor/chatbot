from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from .tools import InternalQAGraphAgentTool, IssueSummaryGraphAgentTool
from .prompt import SUPERVISOR_SYSTEM_PROMPT 
from .state import SuperStateOutput

llm = init_chat_model("gpt-4o", temperature=0)
AIAssistant = create_agent(llm,
                     name="routeragent",
                     tools=[InternalQAGraphAgentTool, IssueSummaryGraphAgentTool], 
                     system_prompt=SUPERVISOR_SYSTEM_PROMPT,
                     response_format=SuperStateOutput
                       )