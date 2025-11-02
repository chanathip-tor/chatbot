from pathlib import Path
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_classic.tools.retriever import create_retriever_tool
from langchain_classic.tools.base import Tool

project_root = Path(__file__).resolve().parents[3]

BUG_REPORTS_DESCRIPTION ="""
Use this tool to **search and retrieve detailed information about system bug reports, technical issues, 
or error cases** identified by developers or QA teams. 

This tool is suitable when the user’s query involves:
- System or application errors (e.g., “email notifications not sent”, “search results incorrect”)
- Backend or frontend bugs and their severities
- Environment-specific problems (web, mobile, backend)
- Technical troubleshooting, root cause, or fixes from the bug reports

The tool returns official structured bug report data including title, description, steps to reproduce, 
environment, and severity.
"""

USER_FEEDBACK_DESCRIPTION ="""
Use this tool to **search and retrieve user feedback, opinions, and comments** collected from customers 
or users of the application.

This tool is suitable when the user’s query involves:
- User complaints, experiences, or suggestions (e.g., “what did users say about the search bar?”)
- Sentiment analysis or recurring pain points from user feedback
- Product usability, satisfaction, or interface experience
- Requests or improvements suggested by users

The tool retrieves unstructured feedback text that reflects user perspectives, 
rather than technical bug descriptions.
"""

## vectorstore_setup
def vectorstore(collection_name: str) -> str:
    vectorstore = Chroma(
        embedding_function=OpenAIEmbeddings(),
        persist_directory=f"{project_root}/vectorstore/chroma_db/{collection_name}",
        collection_name=collection_name
    )
    return vectorstore

## 
def retriever_tool(collection_name: str, description: str, **search_kwargs) -> Tool:
    default_kwargs = {"k": 3}
    default_kwargs.update(search_kwargs) 

    vs = vectorstore(collection_name)
    retrieve = vs.as_retriever(search_kwargs=default_kwargs)
    return create_retriever_tool(
        retrieve,
        f"retrieve_{collection_name}",
        description,

    )

feedback_retriever_tool = retriever_tool("user_feedback", USER_FEEDBACK_DESCRIPTION)
bug_report_retriever_tool = retriever_tool("bug_reports", BUG_REPORTS_DESCRIPTION)
