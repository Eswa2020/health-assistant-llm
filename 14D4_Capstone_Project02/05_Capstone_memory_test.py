# 05_capstone_memory_test.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

# --- Checkpointer: stores conversation state in memory (per session) ---
checkpointer = InMemorySaver()

agent = create_agent(
    model=llm,
    tools=[],  # no tools needed for this memory test
    system_prompt="You are the AfyaPlus Assistant. Remember details the user tells you within this session.",
    checkpointer=checkpointer,
)

# --- Config: thread_id identifies THIS conversation session ---
config = {"configurable": {"thread_id": "patient-session-001"}}

# --- Turn 1: tell the agent something ---
result_1 = agent.invoke(
    {"messages": [HumanMessage(content="My name is Juma and I have a headache.")]},
    config=config,
)
print("Turn 1:", result_1["messages"][-1].content)

# --- Turn 2: ask it to recall, using the SAME thread_id ---
result_2 = agent.invoke(
    {"messages": [HumanMessage(content="What symptom did I mention, and what's my name?")]},
    config=config,
)
print("Turn 2:", result_2["messages"][-1].content)