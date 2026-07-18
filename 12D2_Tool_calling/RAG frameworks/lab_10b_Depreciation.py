# challenge8_depreciation.py
#----------------------------------------------------------------------------------------#
#   The AfyaPlus logistics manager needs straight-line depreciation of clinic 
#                 computers for tax reporting.
# Expand the operational math suite with a validated depreciation tool.
#----------------------------------------------------------------------------------------#
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_core.callbacks import StdOutCallbackHandler
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# --- Tool: Asset depreciation (straight-line) ---
@tool
def calculate_asset_depreciation(initial_cost: float, salvage_value: float, useful_life_years: int) -> str:
    """Calculates annual straight-line depreciation for a clinic asset."""
    if useful_life_years <= 0:
        return "Error: useful life must be greater than zero (cannot divide by zero)."
    annual = (initial_cost - salvage_value) / useful_life_years
    return f"Annual depreciation: {annual:.2f}"


# --- LLM setup ---
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
tools = [calculate_asset_depreciation]

# --- Prompt template: defines the agent's system-level instructions ---
prompt_template = ChatPromptTemplate.from_messages([("system", ("You are the AfyaPlus Logistics Assistant.")),
    ("human", "{input}")])
system_prompt_text = prompt_template.messages[0].prompt.template  # extract system text

# --- Create the agent (bundles prompt + tools + executor logic under the hood) ---
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt_text,
)

# --- Test with a normal query ---
result = agent.invoke(
    {"messages": [HumanMessage(content="What's the annual depreciation for a computer bought at 120,000?")]},
    config={"callbacks": [StdOutCallbackHandler()]}
)
print("\n=== Final Answer ===")
print(result["messages"][-1].content)

print(dict(result))