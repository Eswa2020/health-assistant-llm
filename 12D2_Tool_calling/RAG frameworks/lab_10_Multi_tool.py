# lab10_multi_tool.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_core.callbacks import StdOutCallbackHandler
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# --- Tool 1: Clinic medication stock lookup ---
@tool
def get_clinic_stock_count(medication_name: str) -> str:
    """Returns the current stock count for a medication at the AfyaPlus clinic."""
    stock = {"amoxicillin": 120, "paracetamol": 540}
    return f"{stock.get(medication_name.lower(), 0)} units"


# --- Tool 2: Staff shift cost calculator ---
@tool
def calculate_shift_cost(hours: float, hourly_rate: float) -> str:
    """Calculates the total cost of a staff shift."""
    if hours < 0 or hourly_rate < 0:
        return "Error: hours and rate must be non-negative."
    return f"Shift cost: {hours * hourly_rate:.2f}"


# --- LLM setup ---
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
tools = [get_clinic_stock_count, calculate_shift_cost]

# --- Prompt template: defines the agent's system-level instructions ---
prompt_template = ChatPromptTemplate.from_messages([
    ("system", (
        "You are the AfyaPlus Operations Assistant. "
        "Give clear, concise answers with the correct units (e.g. 'units', currency).")),
    ("human", "{input}"),])
system_prompt_text = prompt_template.messages[0].prompt.template  # extract system text

# --- Create the agent (bundles prompt + tools + LLM ---
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt_text,
)

# --- Invoke with callback so we can watch each reasoning/tool-call step live ---
result = agent.invoke(
    {"messages": [HumanMessage(content="How much paracetamol do we have, and what is the cost of an 8-hour shift at 450 per hour?")]},
    config={"callbacks": [StdOutCallbackHandler()]}
)

print("\n=== Final Answer ===")
print(result["messages"][-1].content)