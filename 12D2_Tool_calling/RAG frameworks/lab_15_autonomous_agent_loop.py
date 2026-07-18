# lab15_autonomous_agent_loop.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.callbacks import StdOutCallbackHandler

from lab_14_bridging_2langchain import query_internal_compliance_vault

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
tools = [query_internal_compliance_vault]

agent = create_agent(model=llm, tools=tools)

# Use a callback to see the agent's reasoning steps
config = {"callbacks": [StdOutCallbackHandler()]}

question = "Do I need director sign-off to buy a $900 centrifuge?"
result = agent.invoke(
    {"messages": [HumanMessage(content=question)]},
config=config)

print("\n--- Final Answer ---")
print(result["messages"][-1].content)