# framework imports
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage
from langgraph.graph import MessagesState
from typing import List, Literal

# module imports
from .prompt import SYSTEM_PROMPT_ROUTER, GRADE_PROMPT, REWRITE_PROMPT, GENERATE_PROMPT
from .state import GradeDocuments
from .tools.retriever import feedback_retriever_tool, bug_report_retriever_tool

response_model = init_chat_model("gpt-4o", temperature=0)
grader_model = init_chat_model("gpt-4o", temperature=0)



def generate_query_or_respond(state: MessagesState):
    """
    Call the model with the routing prompt to decide whether to use a retriever tool
    or directly answer the question.
    """

    routing_prompt = [
        SystemMessage(content=SYSTEM_PROMPT_ROUTER), 
    ] + state["messages"]

    response = (
        response_model
        .bind_tools([feedback_retriever_tool, bug_report_retriever_tool])
        .invoke(  
            routing_prompt
        )
    )

    return {"messages": [response]}



def grade_documents( state: MessagesState, ) -> Literal["generate_answer", "rewrite_question"]:
    """Determine whether the retrieved documents are relevant to the question."""
    question = state["messages"][0].content
    context = state["messages"][-1].content

    prompt = GRADE_PROMPT.format(question=question, context=context)
    response = (
        grader_model
        .with_structured_output(GradeDocuments)
        .invoke(  
            [{"role": "user", "content": prompt}]
        )
    )
    score = response.binary_score

    if score == "yes":
        return "generate_answer"
    else:
        return "rewrite_question"
    

def rewrite_question(state: MessagesState):
    """Rewrite the original user question."""
    messages = state["messages"]
    question = messages[0].content
    prompt = REWRITE_PROMPT.format(question=question)
    response = response_model.invoke([{"role": "user", "content": prompt}])
    return {"messages": [{"role": "user", "content": response.content}]}

def generate_answer(state: MessagesState):
    """Generate an answer."""
    question = state["messages"][0].content
    context = state["messages"][-1].content
    prompt = GENERATE_PROMPT.format(question=question, context=context)
    response = response_model.invoke([{"role": "user", "content": prompt}])
    return {"messages": [response]}