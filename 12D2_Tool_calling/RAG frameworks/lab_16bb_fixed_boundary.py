# fixed_rag.py
# Demonstrates the FIX for the RAG chain that hallucinates.
# The only change: a prompt that forces the model to stay grounded.

import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

# ---- Setup a tiny vector store with one document ----
embeddings = OpenAIEmbeddings()
vector_store = InMemoryVectorStore(embeddings)
vector_store.add_texts([
    "AfyaPlus reimburses staff travel within 30 days of an approved claim."
])
retriever = vector_store.as_retriever()

# ---- FIXED PROMPT: enforces grounding ----
prompt = ChatPromptTemplate.from_template(
    "Answer using ONLY the context below. If the answer is not found, say 'Information not found.'\n\n"
    "Context: {context}\n\nQuestion: {question}"
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# ---- Test ----
if __name__ == "__main__":
    # In-scope: should answer from context
    print("In-scope: How soon is staff travel reimbursed?")
    print(chain.invoke("How soon is staff travel reimbursed?"))

    # Out-of-scope: must refuse
    print("\nOut-of-scope: Best tourist beaches in Mombasa?")
    print(chain.invoke("Best tourist beaches in Mombasa?"))