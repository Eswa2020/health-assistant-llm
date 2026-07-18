# challenge23_pediatric_dosage.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_core.callbacks import StdOutCallbackHandler

load_dotenv()

# Safety disclaimer to append to any final answer
SAFETY_CAUTION = " [CAUTION: This is a computational estimate. A licensed clinician must verify before administration.]"

@tool
def verify_pediatric_weight(age_years: int, weight_kg: float) -> str:
    """Validates if the provided age and weight are within safe pediatric parameters.
    Use this first before any dosage calculation.
    """
    if age_years < 5 and weight_kg > 40:
        return f"Alert: Unusual weight ({weight_kg}kg) for age {age_years}. Human review required."
    return "Patient weight verified as physically plausible."

@tool
def run_dosage_calculation(weight_kg: float) -> str:
    """Calculates baseline fluid requirement (mg) based on weight. Only call after weight verification."""
    dosage = weight_kg * 4.5
    return f"Calculated baseline dose estimate is {dosage} mg."

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
tools = [verify_pediatric_weight, run_dosage_calculation]

system_prompt = (
    "You are a pediatric dosage assistant. "
    "Always use 'verify_pediatric_weight' before 'run_dosage_calculation'. "
    "After the final calculation, append the safety caution: "
    f"'{SAFETY_CAUTION}'"
)

agent = create_agent(model=llm, tools=tools, system_prompt=system_prompt)

# Test with valid parameters
print("=== Test 1: Valid case ===")
result = agent.invoke(
    {"messages": [HumanMessage(content="Calculate dosage for a 4-year-old weighing 18 kg.")]},
    config={"callbacks": [StdOutCallbackHandler()]}
)
print(result["messages"][-1].content)

# Test with suspicious parameters (should trigger alert)
print("\n=== Test 2: Suspicious weight ===")
result = agent.invoke(
    {"messages": [HumanMessage(content="Calculate dosage for a 3-year-old weighing 50 kg.")]},
    config={"callbacks": [StdOutCallbackHandler()]}
)
print(result["messages"][-1].content)