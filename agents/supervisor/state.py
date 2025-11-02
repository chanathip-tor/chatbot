from typing import Literal, Union, Dict, Any
from pydantic import BaseModel, Field

class SuperStateOutput(BaseModel):
    """
    Router agent state storing the selected agent and the reason for selection.
    """
    selected_agent: Literal["InternalQAGraphAgent", "IssueSummaryGraphAgent", "none"] = Field(
        description="The name of the selected agent. Must be one of: 'InternalQAGraphAgent', 'IssueSummaryGraphAgent', or 'none'."
    )
    reason_selection: str = Field(
        description="Explanation of why this agent was chosen."
    )
    final_answer: Union[str, Dict[str, Any]] = Field(
        description="Final answer or structured result returned by the selected agent."
    )