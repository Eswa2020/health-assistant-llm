# lab09_safe_router.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from googlesearch import search  # Google search, no API key

load_dotenv()

# ---------------- Hardcoded Emergency Facilities ----------------
LOCAL_FACILITIES = {
    "kisumu": "Kisumu County Referral Hospital (Emergency Department open 24/7)",
    "nakuru": "Nakuru Level 5 Hospital (Trauma Centre available)",
    "mombasa": "Coast General Teaching & Referral Hospital",
}

# ---------------- Deterministic Router (temperature=0.0) ----------------
router_llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0.0)

router_prompt = ChatPromptTemplate.from_template(
    "Classify this patient message as exactly INFO or EMERGENCY. "
    "EMERGENCY means the patient mentions severe symptoms (chest pain, "
    "trouble breathing, heavy bleeding, stroke signs, etc.) or is in immediate danger. "
    "INFO means everything else (questions about billing, mild symptoms, directions).\n\n"
    "Message: {msg}\n\nAnswer (one word only):"
)
router_chain = router_prompt | router_llm | StrOutputParser()

# ---------------- Google Search Tool (replaces DuckDuckGo) ----------------
@tool
def web_search(query: str) -> str:
    """Search the web for current clinic/hospital information in Kenya. Use for non‑emergency queries."""
    try:
        # Fetch top 3 results, return a concatenated summary
        results = list(search(query, num_results=3))
        if not results:
            return "No results found."
        return "\n".join(results)
    except Exception as e:
        return f"Search failed: {e}"

agent_llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0.0)
tools = [web_search]
info_agent = create_agent(model=agent_llm, tools=tools)

# ---------------- Main Routing Function ----------------
def route_patient_query(user_message: str) -> str:
    route = router_chain.invoke({"msg": user_message}).strip().upper()
    print(f"Router classification: {route}")

    if route == "EMERGENCY":
        for location in LOCAL_FACILITIES:
            if location in user_message.lower():
                return f"[DETERMINISTIC CHAIN ROUTE] Verified Local Facility: {LOCAL_FACILITIES[location]}"
        return ("[DETERMINISTIC CHAIN ROUTE] EMERGENCY PROTOCOL ACTIVATED. "
                "Please call the national emergency line (999) or visit the nearest hospital immediately.")

    # INFO path – dynamic agent with Google search tool
    result = info_agent.invoke({"messages": [HumanMessage(content=user_message)]})
    ai_response = result["messages"][-1].content
    return f"[DYNAMIC AGENT ROUTE] Extracted Info: {ai_response}"

# ---------------- Tests ----------------
if __name__ == "__main__":
    print("=== Test 1: EMERGENCY – chest pain ===")
    print(route_patient_query("My chest hurts badly, I cannot breathe."))
    print("\n" + "="*50 + "\n")

    print("=== Test 2: INFO – find a clinic in Kisumu ===")
    print(route_patient_query("Find me a public hospital in Kisumu, Kenya."))
    print("\n" + "="*50 + "\n")

    print("=== Test 3: EMERGENCY with location ===")
    print(route_patient_query("I am in Nakuru and bleeding heavily."))
    print("\n" + "="*50 + "\n")

    print("=== Test 4: INFO – pharmacy hours ===")
    print(route_patient_query("What time does the AfyaPlus pharmacy close on weekends?"))