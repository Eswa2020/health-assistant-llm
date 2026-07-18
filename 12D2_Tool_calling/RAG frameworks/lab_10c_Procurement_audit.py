# challenge9_Multistep_procurement_audit.py
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
def calculate_facility_utilization(active_beds: int, total_beds: int) -> str:
    """Calculates the capacity utilisation percentage for a clinic ward."""
    if total_beds <= 0:
        return "Error: total beds must be > 0."
    pct = (active_beds / total_beds) * 100
    return f"Utilisation: {pct:.1f}%"

@tool
def calculate_shift_cost(hours: float, hourly_rate: float) -> str:
    """Calculates the total cost of a staff shift."""
    if hours < 0 or hourly_rate < 0:
        return "Error: hours and rate must be non-negative."
    return f"Shift cost: {hours * hourly_rate:.2f}"

@tool
def calculate_asset_depreciation(initial_cost: float, salvage_value: float, useful_life_years: int) -> str:
    """Calculates annual straight-line depreciation for a clinic asset."""
    if useful_life_years <= 0:
        return "Error: useful life must be > 0."
    annual = (initial_cost - salvage_value) / useful_life_years
    return f"Annual depreciation: {annual:.2f}"

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
tools = [calculate_facility_utilization, calculate_shift_cost, calculate_asset_depreciation]

# --- Prompt template ---
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are the AfyaPlus Finance Analyst."),
    ("human", "{input}"),
])
system_prompt_text = prompt_template.messages[0].prompt.template

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt_text,
)

result = agent.invoke(
    {"messages": [HumanMessage(content="80/100 beds occupied — utilisation? Also: 10-hour shift at 300/hr cost, and annual depreciation on a 500,000 machine, salvage 50,000, 5-year life.")]},
    config={"callbacks": [StdOutCallbackHandler()]}
)
print(result["messages"][-1].content)