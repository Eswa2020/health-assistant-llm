# lab_12_rag_pipeline.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from pathlib import Path

load_dotenv()


# ------------------- Ingestion -------------------
# 1. Load the document
# Built another path relative to THIS SCRIPT's location, 
# not the terminal's working directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(SCRIPT_DIR, "lab_12_manual_data", 
                    "operational_guidelines.txt")


loader = TextLoader(file_path, encoding="utf-8")
raw_docs = loader.load()
# 2. Split into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,        # small enough to fit context, large enough to hold meaning
    chunk_overlap=20,      # keep a little overlap so no sentence is split in half(also risk losing meaning)
    separators=["\n\n", "\n", ". ", " ", ""]
)
chunks = splitter.split_documents(raw_docs)
print(f"Loaded {len(raw_docs)} document(s), split into {len(chunks)} chunks.")

# 3. Embed and persist in Chroma
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
vector_store = Chroma.from_documents(
    documents=chunks,
    embedding=embedding_model,
    persist_directory="./chroma_db"       # will survive restarts
)
# No need to call persist() explicitly with from_documents, but it's saved.

# -------------------- Retriever --------------------
# 4. Create a retriever with k = 3 (bring back 3 most relevant outputs))
retriever = vector_store.as_retriever(search_kwargs={"k": 3})

# -------------------- RAG Chain --------------------
def format_docs(docs):
    """Join all retrieved document texts into one string."""
    return "\n\n".join(doc.page_content for doc in docs)

prompt = ChatPromptTemplate.from_template(
    "Answer using ONLY the context below. If the answer is not found, say 'Information not found.'\n\n"
    "Context: {context}\n\nQuestion: {question}"
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# -------------------- Test --------------------
if __name__ == "__main__":
    question = "How soon is staff travel reimbursed?"
    print(f"Question: {question}")
    answer = rag_chain.invoke(question)
    print(f"Answer: {answer}")