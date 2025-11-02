from pathlib import Path
import os
import re
import shutil
import json
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document


from logging import basicConfig, getLogger, INFO
from load_dotenv import load_dotenv
load_dotenv()



parents = Path(__file__).resolve().parents[0]

basicConfig(level=INFO)
logger = getLogger(__name__)

# ----------------------------
# Helper: Read text file
# ----------------------------
def get_data(file_path: str) -> str:
    with open(file_path, encoding="utf-8") as f:
        text = f.read()
    return text


def clear_collection_dir(persist_directory:  str):
    """Clear all files under persist_directory for a given collection."""
    persist_directory = Path(persist_directory)
    if persist_directory.exists() and persist_directory.is_dir():
        logger.info(f"Clear old vectorstore: {persist_directory}")
        shutil.rmtree(persist_directory)
    else:
        logger.info(f"No existing directory to clear for: {persist_directory}")

def build_vectorstore(collection_name: str, docs: list[Document], persist_directory: str ):
    """Clear old collection folder, then build new vectorstore"""

    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=OpenAIEmbeddings(),
        persist_directory=persist_directory,
        collection_name=collection_name,
    )
    logger.info(f"✅ Created new vectorstore: {collection_name} ")
    logger.info(f"✅ Total records in the collection: {len(vectorstore.get()["documents"])}")
    logger.info(f"----------")
    return vectorstore


# ----------------------------
# Create Bug Report Vectorstore
# ----------------------------
def bug_report_vectorstore(reset: bool = True, 
                                    file_name: str = "ai_test_bug_report.txt", 
                                    collection_name: str = "bug_reports" ):

    # declare
    persist_directory = f"{parents}/chroma_db/{collection_name}"
    file_path = f"{parents}/data/{file_name}"

    # get text
    logger.info(f"ℹ️ Creating {collection_name} Vectorstore...")
    logger.info(f"ℹ️ Getting data from {file_path}")
    text = get_data(file_path)

    # clean text
    logger.info("⏳ Cleaning text...")
    clean_text = text.replace("\ufeff", "").strip()
    bug_report = [b.strip() for b in re.split(r"(?=Bug #\d+)", clean_text) if b.strip()]

    logger.info("⏳ Creating documents...")
    bug_report_docs = [
        Document(
            page_content=re.sub(r"Bug #(\d+)", "", b).strip(),
            metadata={"id": re.search(r"Bug #(\d+)", b).group(1)},
        )
        for b in bug_report
    ]

    preview = [
        {"id": d.metadata["id"], "content": d.page_content[:60] + "..."}
        for d in bug_report_docs[:2]
    ]
    logger.info(
        "documents preview:\n%s", json.dumps(preview, indent=2)
    )

    # add vectorstore
    if reset :
        clear_collection_dir(persist_directory)
    
    vectorstore = build_vectorstore(collection_name, bug_report_docs, persist_directory)

    
    return vectorstore


# ----------------------------
# Create User Feedback Vectorstore
# ----------------------------
def user_feedback_vectorstore(reset: bool = True, 
                                       file_name: str = "ai_test_user_feedback.txt",
                                       collection_name: str = "user_feedback" ):
    
   # declare
    persist_directory = f"{parents}/chroma_db/{collection_name}"
    file_path = f"{parents}/data/{file_name}"

    # get text
    logger.info(f"ℹ️ Creating {collection_name} Vectorstore...")
    logger.info(f"ℹ️ Getting data from {file_path}")
    text = get_data(file_path)

    # clean text
    logger.info("⏳ Cleaning text...")
    clean_text = text.replace("\ufeff", "").strip()
    # แยกแต่ละ feedback
    user_feedback = [
        fb.strip()
        for fb in re.split(r"(?=Feedback #\d+)", clean_text)
        if re.search(r"^Feedback #\d+", fb.strip())
    ]
    logger.info("⏳ Creating documents...")
    user_feedback_docs = [
        Document(
            page_content=re.sub(r"Feedback #(\d+):", "", b).strip(),
            metadata={"id": re.search(r"Feedback #(\d+)", b).group(1)},
        )
        for b in user_feedback
    ]

    preview = [
        {"id": d.metadata["id"], "content": d.page_content[:60] + "..."}
        for d in user_feedback_docs[:2]
    ]
    logger.info(
        "documents preview:\n%s", json.dumps(preview, indent=2)
    )

    # add vectorstore
    if reset :
        clear_collection_dir(persist_directory)
    
    vectorstore = build_vectorstore(collection_name, user_feedback_docs, persist_directory)
    return vectorstore

if __name__ == "__main__":
    bug_vs = bug_report_vectorstore()
    feedback_vs = user_feedback_vectorstore()
