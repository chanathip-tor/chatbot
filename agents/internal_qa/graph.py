from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from langgraph.graph import MessagesState
from .node import (
    generate_query_or_respond,
    grade_documents,
    rewrite_question,
    generate_answer,
)
from .tools.retriever import feedback_retriever_tool, bug_report_retriever_tool

builder = StateGraph(MessagesState)

# Define the nodes we will cycle between
builder.add_node(generate_query_or_respond)
builder.add_node("retrieve", ToolNode([feedback_retriever_tool, bug_report_retriever_tool]))
builder.add_node(rewrite_question)
builder.add_node(generate_answer)

builder.add_edge(START, "generate_query_or_respond")

# Decide whether to retrieve
builder.add_conditional_edges(
    "generate_query_or_respond",
    # Assess LLM decision (call `retriever_tool` tool or respond to the user)
    tools_condition,
    {
        # Translate the condition outputs to nodes in our graph
        "tools": "retrieve",
        END: END,
    },
)

# Edges taken after the `action` node is called.
builder.add_conditional_edges(
    "retrieve",
    # Assess agent decision
    grade_documents,
)
builder.add_edge("generate_answer", END)
builder.add_edge("rewrite_question", "generate_query_or_respond")

# Compile
InternalQAGraphAgent = builder.compile()