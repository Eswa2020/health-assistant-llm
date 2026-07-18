# lab09_safe_router.py
# =============================================================================
# AFYAPLUS – Challenge 6: Safe Clinic Router Matrix + Debugging Fix
# =============================================================================
# Demonstrates a safety‑critical router:
#   - Deterministic gate: INFO → dynamic agent, EMERGENCY → hardcoded path.
#   - Router uses temperature=0.0 for repeatable classification.
#   - Agent uses a web search tool for non‑emergency queries.
# =============================================================================

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools import DuckDuckGoSearchRun

load_dotenv()

# ---------------- Hardcoded Emergency Facilities ----------------
LOCAL_FACILITIES = {
    "kisumu": "Kisumu County Referral Hospital (Emergency Department open 24/7)",
    "nakuru": "Nakuru Level 5 Hospital (Trauma Centre available)",
    "mombasa": "Coast General Teaching & Referral Hospital",
}

# ---------------- Deterministic Router (temperature=0.0) ----------------
# Fix for the "Router That Always Says BILLING" bug:
#   set temperature=0.0 to make the classification repeatable.
router_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
router_prompt = ChatPromptTemplate.from_template(
    "Classify this patient message as exactly INFO or EMERGENCY. "
    "EMERGENCY means the patient mentions severe symptoms (chest pain, "
    "trouble breathing, heavy bleeding, stroke signs, etc.) or is in immediate danger. "
    "INFO means everything else (questions about billing, mild symptoms, directions).\n\n"
    "Message: {msg}\n\nAnswer (one word only):"
)
router_chain = router_prompt | router_llm | StrOutputParser()

# ---------------- Dynamic Agent (for INFO queries) ----------------
search_tool = DuckDuckGoSearchRun()
# We wrap the search in a LangChain tool for the agent
@tool
def web_search(query: str) -> str:
    """Search the web for current clinic information. Use for non‑emergency location queries."""
    return search_tool.run(query)

agent_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
tools = [web_search]
info_agent = create_agent(model=agent_llm, tools=tools)

# ---------------- Main Routing Function ----------------
def route_patient_query(user_message: str) -> str:
    # Step 1: Classify as INFO or EMERGENCY
    route = router_chain.invoke({"msg": user_message}).strip().upper()
    print(f"Router classification: {route}")

    # Step 2: Deterministic emergency path – hardcoded
    if route == "EMERGENCY":
        # Check if a location name is mentioned for fast lookup
        for location in LOCAL_FACILITIES:
            if location in user_message.lower():
                return f"[DETERMINISTIC CHAIN ROUTE] Verified Local Facility: {LOCAL_FACILITIES[location]}"
        # Generic emergency response
        return ("[DETERMINISTIC CHAIN ROUTE] EMERGENCY PROTOCOL ACTIVATED. "
                "Please call the national emergency line (999) or visit the nearest hospital immediately.")

    # Step 3: Dynamic agent path for INFO queries
    result = info_agent.invoke(
        {"messages": [HumanMessage(content=user_message)]}
    )
    ai_response = result["messages"][-1].content
    return f"[DYNAMIC AGENT ROUTE] Extracted Info: {ai_response}"

# ---------------- Test Executions ----------------
if __name__ == "__main__":
    print("=== Test 1: EMERGENCY – chest pain (should be hardcoded) ===")
    print(route_patient_query("My chest hurts badly, I cannot breathe."))
    print("\n" + "="*50 + "\n")

    print("=== Test 2: INFO – ask about a location (should use agent) ===")
    print(route_patient_query("Which clinics are open in Kisumu today?"))
    print("\n" + "="*50 + "\n")

    print("=== Test 3: EMERGENCY with location (hardcoded lookup) ===")
    print(route_patient_query("I am in Nakuru and bleeding heavily."))
    print("\n" + "="*50 + "\n")

    print("=== Test 4: INFO – simple question ===")
    print(route_patient_query("What time does the pharmacy close?"))