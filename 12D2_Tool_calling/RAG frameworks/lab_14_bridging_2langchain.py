# lab_14_bridging_2langchain.py
import os
from dotenv import load_dotenv
from langchain_core.tools import tool



# Import the engine from the ingestion script
from lab_13b__ingestion import base_query_engine

load_dotenv()

print("--- Step 4: Binding LlamaIndex Query Engine to LangChain Interface ---")

@tool
def query_internal_compliance_vault(user_search_query: str) -> str:
    """Queries the internal AfyaPlus regional compliance protocols database.
    Use this tool whenever the user asks questions regarding company regulations,
    employee financial limits, medical allowances, or operational clinic metadata.
    """
    try:
        engine_response = base_query_engine.query(user_search_query)
        return str(engine_response)
    except Exception as error:
        return f"Database Retrieval failure encountered: {str(error)}"

if __name__ == "__main__":
    print("\nExecuting Tool Invocations Directly via LangChain Interface...")
    tool_payload = {"user_search_query": "Nairobi hub outpatient medical allowance limits"}
    result = query_internal_compliance_vault.invoke(tool_payload)
    print(f"\nWrapped Tool Result Output:\n{result}")