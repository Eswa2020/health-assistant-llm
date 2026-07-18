# challenge12_procurement.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

# 1. Setup
embeddings = OpenAIEmbeddings()
vector_store = InMemoryVectorStore(embeddings)

# 2. Add BOTH the original policy AND the new procurement policy
vector_store.add_texts([
    "AfyaPlus reimburses staff travel within 30 days of an approved claim.",
    "Clinic equipment purchases above $500 require director sign-off.",
    "Procurement Policy: For any logistics hardware purchase exceeding $1,000, the Chief Operations Officer must approve."
])

retriever = vector_store.as_retriever()

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

prompt = ChatPromptTemplate.from_template(
    "Answer using ONLY the context below. If the answer is not in the context, say 'Information not found.'\n\n"
    "Context: {context}\n\nQuestion: {question}"
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser())

# 3. Test with a query that requires the new procurement policy
print("=== Challenge 12 Test ===")
response = rag_chain.invoke(
    "What approval signature is needed for a logistics hardware purchase of $1,500?"
)
print(response)