# challenge22_boundary.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.callbacks import StdOutCallbackHandler

load_dotenv()

@tool
def compliance_query(question: str) -> str:
    """Answers policy questions. Use for company rules."""
    return "Policy: purchases above $500 require director sign-off."

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
tools = [compliance_query]

# The system prompt enforces boundary refusal
system_prompt = (
    "You are a helpful assistant. Use the tools provided. "
    "If a question cannot be answered with the available tools or information, "
    "reply exactly: 'Information not found.' Do not guess."
)

agent = create_agent(model=llm, tools=tools, system_prompt=system_prompt)

# Out-of-boundary request
question = "What is the weather like in Mombasa today?"
result = agent.invoke(
    {"messages": [HumanMessage(content=question)]},
    config={"callbacks": [StdOutCallbackHandler()]}
)
print("Agent response:", result["messages"][-1].content)