# challenge14_fallback.py
import os
import logging
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ---- Paths (relative to this script) ----
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
primary_path = os.path.join(SCRIPT_DIR, "lab_12_manual_data", "operational_guidelines.txt")
backup_path  = os.path.join(SCRIPT_DIR, "lab_12_manual_data", "backup_guidelines.txt")

def run_resilient_ingestion():
    docs = []
    # 1. Try primary
    try:
        loader = TextLoader(primary_path, encoding="utf-8")
        docs = loader.load()
        logging.info(f"Loaded {len(docs)} doc(s) from primary: {primary_path}")
    except FileNotFoundError:
        logging.warning(f"Primary file not found: {primary_path}. Attempting backup.")
        # 2. Try backup
        try:
            loader = TextLoader(backup_path, encoding="utf-8")
            docs = loader.load()
            logging.info(f"Loaded {len(docs)} doc(s) from backup: {backup_path}")
        except FileNotFoundError:
            raise RuntimeError("Both primary and backup files missing. Cannot proceed.")
    return docs

if __name__ == "__main__":
    try:
        documents = run_resilient_ingestion()
        print(f"Successfully loaded {len(documents)} document(s).")
    except RuntimeError as e:
        print(f"ERROR: {e}")