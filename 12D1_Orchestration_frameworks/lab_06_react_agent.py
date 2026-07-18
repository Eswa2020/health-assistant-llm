# lab6_react_agent.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_core.callbacks import StdOutCallbackHandler  # NEW

load_dotenv()

@tool
def get_clinic_stock_count(medication_name: str) -> str:
    """Returns current stock for a medication at the AfyaPlus clinic."""
    stock = {"amoxicillin": 120, "paracetamol": 540}
    return f"{stock.get(medication_name.lower(), 0)} units"

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
tools = [get_clinic_stock_count]

# Create agent (NO verbose param!)
agent = create_agent(model=llm, tools=tools)

# To see the agent's thinking, we attach a callback handler
result = agent.invoke(
    {"messages": [HumanMessage(content="Do we have enough amoxicillin in stock?")]},
    config={"callbacks": [StdOutCallbackHandler()]}
)

# The final response is the last message
print("\n=== Final Answer ===")
print(result["messages"][-1].content)