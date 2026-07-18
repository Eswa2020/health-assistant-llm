# lab_10dd_supplier_routing.py
import os
from dotenv import load_dotenv
from typing import Literal
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# --- Tool 1: Determine storage facility (flexible input — category is free text) ---
@tool
def determine_storage_facility(item_category: str) -> str:
    """Given an item category, returns the correct storage facility and its section code.
    Cold-chain items go to Refrigerated Depot, Section X.
    All other items go to General Inventory Depot, Section Y."""
    if "cold-chain" in item_category.lower() or "cold chain" in item_category.lower():
        return "Refrigerated Depot, Section X (section_code: section_x)"
    else:
        return "General Inventory Depot, Section Y (section_code: section_y)"


# --- Tool 2: Deterministic router — only two valid inputs allowed ---
@tool
def lookup_inventory_representative(section_code: Literal["section_x", "section_y"]) -> str:
    """Returns the representative responsible for a given section.
    section_x -> Representative Mwangi (Refrigerated Depot)
    section_y -> Representative Otieno (General Inventory Depot)
    section_code must be exactly 'section_x' or 'section_y' — no other values are valid."""
    mapping = {
        "section_x": "Representative Mwangi",
        "section_y": "Representative Otieno",
    }
    return mapping[section_code]


# --- LLM setup ---
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
tools = [determine_storage_facility, lookup_inventory_representative]

# --- Prompt template ---
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are the AfyaPlus Logistics Coordinator."),
    ("human", "{input}"),
])
system_prompt_text = prompt_template.messages[0].prompt.template

# --- Create the agent ---
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt_text,
)

if __name__ == "__main__":
    query = "We have a shipment of cold-chain items arriving. Who is the active inventory representative we should contact at their assigned facility?"
    result = agent.invoke({"messages": [HumanMessage(content=query)]})
    print(f"\nFinal System Resolution:\n{result['messages'][-1].content}")