# challenge5_stateful_agent.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

@tool
def get_clinic_stock_count(medication_name: str) -> str:
    """Returns current stock for a medication at AfyaPlus."""
    stock = {"amoxicillin": 120, "paracetamol": 540}
    return f"{stock.get(medication_name.lower(), 0)} units"

@tool
def lookup_specialist_department(specialty_name: str) -> str:
    """Find the location and status of a medical specialty department."""
    roster = {"pediatrics": "Wing A, open until 8 PM.", "cardiology": "Main Tower, requires pre-booking."}
    return roster.get(specialty_name.lower(), f"No info for {specialty_name}.")

@tool
def check_appointment_availability(doctor_name: str) -> str:
    """Check if a specific doctor has available slots this week."""
    schedule = {"dr. otieno": "3 slots on Thursday", "dr. wanjiku": "Fully booked"}
    return schedule.get(doctor_name.lower(), "Doctor not found.")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=1.3)
tools = [get_clinic_stock_count, lookup_specialist_department, check_appointment_availability]

agent = create_agent(model=llm, tools=tools)

history = []

def chat(user_input):
    history.append(HumanMessage(content=user_input))
    result = agent.invoke({"messages": history})
    ai_response = result["messages"][-1].content
    history.append(AIMessage(content=ai_response))
    return ai_response

# ---- Tests ----
print("=== Turn 1 ===")
print(chat("My name is Eswaq. Do we have rash creams?"))

print("\n=== Turn 2 ===")
print(chat("What is my name, and which hospital,department and doctor available?"))

print("=== Turn 3 ===")
print(chat("My name is Baraka. Do we have amoxicillin?"))

print("\n=== Turn 4 ===")
print(chat("What is my name, and which department for a child's fever?"))
