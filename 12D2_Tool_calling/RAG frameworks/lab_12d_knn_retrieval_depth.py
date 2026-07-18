# challenge16_depth.py
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(SCRIPT_DIR, "lab_12_manual_data", "operational_guidelines.txt")

# ---- Ingestion (reuse same pipeline) ----
loader = TextLoader(file_path, encoding="utf-8")
raw_docs = loader.load()
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", ". ", " ", ""]
)
chunks = splitter.split_documents(raw_docs)

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
vector_store = Chroma.from_documents(
    documents=chunks,
    embedding=embedding_model,
    persist_directory="./chroma_db_depth"   # separate folder to avoid conflict
)

def retrieve_with_k(k, query):
    retriever = vector_store.as_retriever(search_kwargs={"k": k})
    retrieved_docs = retriever.invoke(query)
    print(f"\n--- k = {k} ---")
    for i, doc in enumerate(retrieved_docs):
        print(f"  Doc {i+1}: {doc.page_content[:100]}...")
    return retrieved_docs

if __name__ == "__main__":
    query = "What is the travel reimbursement policy and who approves equipment purchases?"
    print(f"Query: {query}")
    retrieve_with_k(1, query)
    retrieve_with_k(3, query)
    retrieve_with_k(5, query)