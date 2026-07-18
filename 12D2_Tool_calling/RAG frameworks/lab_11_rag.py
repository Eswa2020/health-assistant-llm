# lab11_rag.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

# 1. Embedding model + vector store
embeddings = OpenAIEmbeddings()
vector_store = InMemoryVectorStore(embeddings)

# 2. Add documents (the injection phase)
vector_store.add_texts([
    "AfyaPlus reimburses staff travel within 30 days of an approved claim.",
    "Clinic equipment purchases above $500 require director sign-off."
])

# 3. Retriever – returns a list of Document objects
retriever = vector_store.as_retriever()

# 4. Helper to join document texts into one string
def format_docs(docs):return "\n\n".join(doc.page_content for doc in docs)

# 5. Prompt – enforces grounding (answer only from context)
prompt = ChatPromptTemplate.from_template(
    "Answer using ONLY the context below. If the answer is not in the context, say 'Information not found.'\n\n"
    "Context: {context}\n\nQuestion: {question}"
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

# 6. RAG chain (retrieve → format → prompt → LLM → text)
rag_chain = ({"context": retriever
              , "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 7. Test with a question that should be answered
print("=== Lab 11 Test ===")
response = rag_chain.invoke("How soon is staff travel reimbursed?")
print(response)