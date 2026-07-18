# challenge8_depreciation.py
#----------------------------------------------------------------------------------------#
#   The AfyaPlus logistics manager needs straight-line depreciation of clinic 
#   computers for tax reporting, plus facility utilisation tracking as part 
#   of the expanded operation
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

# --- Tool 1: Asset depreciation (straight-line) ---
@tool
def calculate_asset_depreciation(initial_cost: float, salvage_value: float, useful_life_years: int) -> str:
    """Calculates annual straight-line depreciation for a clinic asset."""
    if useful_life_years <= 0:
        return "Error: useful life must be positive; division by zero is prohibited."
    annual = (initial_cost - salvage_value) / useful_life_years
    return f"Annual depreciation: {annual:.2f}"


# --- Tool 2: Facility utilisation ---
@tool
def calculate_facility_utilization(active_beds: int, total_beds: int) -> str:
    """Calculates the capacity utilisation percentage for a clinic ward."""
    try:
        if total_beds <= 0:
            return "Error: total beds must be greater than zero."
        pct = (active_beds / total_beds) * 100
        return f"Utilisation: {pct:.1f}%"
    except Exception:
        return "Error: could not compute utilisation."


# --- LLM setup ---
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
tools = [calculate_asset_depreciation, calculate_facility_utilization]

# --- Prompt template: defines the agent's system-level instructions ---
prompt_template = ChatPromptTemplate.from_messages([
("system",("You are the AfyaPlus Finance Analyst")),
("human", "{input}"),])
system_prompt_text = prompt_template.messages[0].prompt.template  # extract system text

# --- Create the agent (bundles prompt + tools + LLM) ---
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt_text,
)

# --- Test 1: single-question query (depreciation only) ---
print("=== Test 1: Single Question (Depreciation Only) ===")
result_1 = agent.invoke(
    {"messages": [HumanMessage(content="What's the annual depreciation for a computer bought at 120,000, salvage value 20,000, lifespan 4 years?")]},
    config={"callbacks": [StdOutCallbackHandler()]}
)
print("\n--- Final Answer ---")
print(result_1["messages"][-1].content)

# --- Test 2: multi-part question (bed capacity + equipment depreciation) ---
print("\n\n=== Test 2: Multi-Part Question (Cancer Wing Capacity + Monitoring Equipment) ===")
result_2 = agent.invoke(
    {"messages": [HumanMessage(content=(
        "I'm doing a quarterly analysis for the cancer wing. Can you tell me our "
        "current bed capacity utilisation . we have 18 active beds out of 25 total? "
        "Also, we bought new patient monitoring equipment for 450,000, expected "
        "salvage value of 50,000, with a useful life of 5 years — what's the annual "
        "depreciation on that equipment?"
    ))]},
    config={"callbacks": [StdOutCallbackHandler()]}
)
print("\n--- Final Answer ---")
print(result_2["messages"][-1].content)