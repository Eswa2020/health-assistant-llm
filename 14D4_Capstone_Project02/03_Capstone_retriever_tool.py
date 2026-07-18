# capstone_retriever_tool.py
import os
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI as LlamaOpenAI
from langchain_core.tools import tool

load_dotenv()

# --- Configure LlamaIndex ---
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
Settings.llm = LlamaOpenAI(model="gpt-4o-mini", temperature=0.0)

# --- Build path relative to this script ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_DIR = os.path.join(SCRIPT_DIR, "knowledge_manual")

# --- Load documents and build the index once, at import time ---
documents = SimpleDirectoryReader(KNOWLEDGE_DIR).load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()


# --- Wrap the LlamaIndex query engine as a LangChain @tool ---
@tool
def query_clinic_guidelines(question: str) -> str:
    """Searches the AfyaPlus operational guidelines knowledge base to answer
    questions about clinic policies — e.g. medication stock levels, shift
    management, procurement rules, or travel reimbursement. Always use this
    tool when a question relates to clinic operational policy rather than
    guessing an answer."""
    try:
        response = query_engine.query(question)
        return str(response)
    except Exception as e:
        return f"Error retrieving guideline information: {e}"


# --- Quick standalone test ---
if __name__ == "__main__":
    test_questions = [
        "What is the medication stock policy?",
        "How are travel reimbursements processed?",
        "What is the night-shift pay premium?",
    ]
    for q in test_questions:
        print(f"\nQ: {q}")
        print(f"A: {query_clinic_guidelines.invoke({'question': q})}")