# challenge15_tuning.py
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(SCRIPT_DIR, "lab_12_manual_data", "operational_guidelines.txt")

def test_splitter(chunk_size, chunk_overlap, label):
    loader = TextLoader(file_path, encoding="utf-8")
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_documents(docs)
    print(f"\n--- {label} (size={chunk_size}, overlap={chunk_overlap}) ---")
    print(f"Number of chunks: {len(chunks)}")
    
    # Print first 2 chunks (first 120 chars each)
    for i, chunk in enumerate(chunks[:2]):
        print(f"Chunk {i+1}: {chunk.page_content[:120]}...")

if __name__ == "__main__":
    # Option A: small chunks
    test_splitter(200, 30, "Option A (small)")
    # Option B: larger chunks
    test_splitter(500, 80, "Option B (large)")
    # Option C: your current setting from lab_12
    test_splitter(500, 50, "Option C (lab default)")