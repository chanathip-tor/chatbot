from typing import List, Literal
from pydantic import BaseModel, Field
from typing import TypedDict

# structured output models
class ReportedIssueOut(BaseModel):
    reported_issue: str = Field(description="Extract a single-sentence symptom-focused summary from the first-person complaint; drop stack traces/IDs/URLs; avoid causes unless stated by users; ≤ 20 tokens.")

class AffectedComponentsOut(BaseModel):
    affected_components: List[str] = Field(description="Find feature/module mentions and normalize to canonical taxonomy (e.g., 'email'→'notification-service', 'search bar'→'search'); dedupe; return list [].")

class SeverityOut(BaseModel):
    severity: Literal["Blocker","High","Medium","Low"]


# Graph state
class State(TypedDict):
    issue_text: str
    reported_issue: ReportedIssueOut
    affected_components: AffectedComponentsOut
    severity: SeverityOut

class OutputState(TypedDict):
    reported_issue: ReportedIssueOut
    affected_components: AffectedComponentsOut
    severity: SeverityOut





