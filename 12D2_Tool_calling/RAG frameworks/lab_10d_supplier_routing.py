# challenge10_supplier_routing.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_core.callbacks import StdOutCallbackHandler
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

@tool
def determine_storage_facility(item_category: str) -> str:
    """Given an item category, returns the correct storage facility.
    Cold-chain items go to Refrigerated Depot - Section X.
    All other items go to General Inventory Depot - Section Y."""
    if "cold-chain" in item_category.lower() or "cold chain" in item_category.lower():
        return "Refrigerated Depot - Section X"
    else:
        return "General Inventory Depot - Section Y"


@tool
def lookup_inventory_representative(section: str) -> str:
    """Returns the representative responsible for a given section.
    Section X -> Representative Mwangi
    Section Y -> Representative Otieno"""
    mapping = {
        "section x": "Representative Mwangi",
        "section y": "Representative Otieno"
    }
    section_lower = section.lower()
    for key, rep in mapping.items():
        if key in section_lower:
            return rep
    return "No representative found."

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

# --- Prompt template ---
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are the AfyaPlus Logistics Coordinator."),
    ("human", "{input}"),])
system_prompt_text = prompt_template.messages[0].prompt.template

# TODO: Step 3 - Wire tools into an array, initialize the agent executor, and run the compound test query
tools = [determine_storage_facility, lookup_inventory_representative]

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt_text,
)

result = agent.invoke(
    {"messages": [HumanMessage(content="We need to ship some cold-chain items. Which storage facility should they go to, and who is the contact person for that facility?")]},
    config={"callbacks": [StdOutCallbackHandler()]}
)
print(result["messages"][-1].content)