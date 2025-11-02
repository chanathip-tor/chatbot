from langgraph.graph import StateGraph, START, END


from .state import State, OutputState
from .node import llm_reported_issue, llm_affected_components, llm_severity
# Build workflow
builder = StateGraph(State, output_schema=OutputState)

# Add nodes
builder.add_node("llm_reported_issue", llm_reported_issue)
builder.add_node("llm_affected_components", llm_affected_components)
builder.add_node("llm_severity", llm_severity)

# Add edges to connect nodes
builder.add_edge(START, "llm_reported_issue")
builder.add_edge(START, "llm_affected_components")
builder.add_edge(START, "llm_severity")
builder.add_edge("llm_reported_issue", END)
builder.add_edge("llm_affected_components", END)
builder.add_edge("llm_severity", END)


IssueSummaryGraphAgent = builder.compile()

