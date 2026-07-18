# lab9_math_suite.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_core.callbacks import StdOutCallbackHandler
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# --- Tool: Facility utilisation ---
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
tools = [calculate_facility_utilization]

# --- Prompt template: defines the agent's system-level instructions ---
prompt_template = ChatPromptTemplate.from_messages([
    ("system", ("You are an AfyaPlus operations assistant.")),
    ("human", "{input}"),])
system_prompt_text = prompt_template.messages[0].prompt.template  # extract system text

# --- Create the agent (bundles prompt + tools + LLM) ---

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt_text,
)

# --- Invoke with callback so we can watch each reasoning/tool-call step live ---
result = agent.invoke(
    {"messages": [HumanMessage(content="If 84 of our 100 beds are occupied, what is utilisation?")]},
    config={"callbacks": [StdOutCallbackHandler()]}
)

print("\n=== Final Answer ===")
print(result["messages"][-1].content)