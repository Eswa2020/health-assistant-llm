# capstone_llamaindex_pipeline.py
import os
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI as LlamaOpenAI

load_dotenv()

# --- Configure LlamaIndex to use OpenAI for embeddings + LLM ---
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
Settings.llm = LlamaOpenAI(model="gpt-4o-mini", temperature=0.0)

# --- Build path relative to this script, not the terminal's working directory ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_DIR = os.path.join(SCRIPT_DIR, "knowledge_manual")

# --- Load documents from the knowledge-manual directory ---
documents = SimpleDirectoryReader(KNOWLEDGE_DIR).load_data()
print(f"Loaded {len(documents)} document(s) from {KNOWLEDGE_DIR}")

# --- Build the vector index (embeds and stores in memory by default) ---
index = VectorStoreIndex.from_documents(documents)
print("Vector index built successfully.")

# --- Quick standalone test: query the index directly ---
if __name__ == "__main__":
    query_engine = index.as_query_engine()
    test_query = "What is the medication stock policy?"
    response = query_engine.query(test_query)
    print(f"\nTest query: {test_query}")
    print(f"Response: {response}")