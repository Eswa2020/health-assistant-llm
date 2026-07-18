# 06_Capstone_full_pipeline.py
import os
import re
import uuid
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.embeddings.openai import OpenAIEmbedding as LlamaOpenAIEmbedding
from llama_index.llms.openai import OpenAI as LlamaOpenAI

load_dotenv()

# ============================================================
# 1. PRIVACY-MASKING MIDDLEWARE
# ============================================================
def mask_pii(text: str) -> tuple[str, dict]:
    pii_map = {}
    phone_pattern = re.compile(r"(?:\+254|254|0)(7|1)\d{8}")
    email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

    def replace_phone(match):
        token = f"<PHONE_{uuid.uuid4().hex[:8]}>"
        pii_map[token] = match.group(0)
        return token

    def replace_email(match):
        token = f"<EMAIL_{uuid.uuid4().hex[:8]}>"
        pii_map[token] = match.group(0)
        return token

    masked_text = email_pattern.sub(replace_email, text)
    masked_text = phone_pattern.sub(replace_phone, masked_text)
    return masked_text, pii_map


def unmask_pii(text: str, pii_map: dict) -> str:
    for token, original_value in pii_map.items():
        text = text.replace(token, original_value)
    return text


# ============================================================
# 2. LLAMAINDEX GROUNDED RETRIEVER TOOL
# ============================================================
Settings.embed_model = LlamaOpenAIEmbedding(model="text-embedding-3-small")
Settings.llm = LlamaOpenAI(model="gpt-4o-mini", temperature=0.0)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_DIR = os.path.join(SCRIPT_DIR, "knowledge_manual")

_documents = SimpleDirectoryReader(KNOWLEDGE_DIR).load_data()
_index = VectorStoreIndex.from_documents(_documents)
_query_engine = _index.as_query_engine()


@tool
def query_clinic_guidelines(question: str) -> str:
    """Searches the AfyaPlus operational guidelines knowledge base to answer
    questions about clinic policies — e.g. medication stock levels, shift
    management, procurement rules, or travel reimbursement."""
    try:
        return str(_query_engine.query(question))
    except Exception as e:
        return f"Error retrieving guideline information: {e}"


# ============================================================
# 3. DYNAMIC FUNCTIONAL TOOLS (clinical calculations)
# ============================================================
@tool
def calculate_medication_dosage(patient_weight_kg: float, dose_per_kg_mg: float) -> str:
    """Calculates total medication dose (mg) from patient weight and a
    weight-based dosing rate (mg per kg)."""
    try:
        if patient_weight_kg <= 0:
            return "Error: patient weight must be greater than zero."
        if dose_per_kg_mg <= 0:
            return "Error: dose per kg must be greater than zero."
        total_dose_mg = patient_weight_kg * dose_per_kg_mg
        return f"Total dose: {total_dose_mg:.2f} mg for a {patient_weight_kg:.1f} kg patient."
    except Exception as e:
        return f"Error calculating dosage: {e}"


@tool
def calculate_iv_drip_rate(volume_ml: float, infusion_time_hours: float, drop_factor_gtts_per_ml: float = 20.0) -> str:
    """Calculates IV infusion drip rate (drops/min) from volume, infusion
    time, and IV set drop factor."""
    try:
        if volume_ml <= 0:
            return "Error: volume must be greater than zero."
        if infusion_time_hours <= 0:
            return "Error: infusion time must be greater than zero."
        if drop_factor_gtts_per_ml <= 0:
            return "Error: drop factor must be greater than zero."
        infusion_time_minutes = infusion_time_hours * 60
        drip_rate = (volume_ml * drop_factor_gtts_per_ml) / infusion_time_minutes
        return f"IV drip rate: {drip_rate:.1f} drops/min (gtts/min)."
    except Exception as e:
        return f"Error calculating drip rate: {e}"


@tool
def calculate_bmi(weight_kg: float, height_m: float) -> str:
    """Calculates BMI from weight (kg) and height (m), with WHO classification."""
    try:
        if weight_kg <= 0:
            return "Error: weight must be greater than zero."
        if height_m <= 0:
            return "Error: height must be greater than zero."
        bmi = weight_kg / (height_m ** 2)
        category = "Underweight" if bmi < 18.5 else "Normal weight" if bmi < 25 else "Overweight" if bmi < 30 else "Obese"
        return f"BMI: {bmi:.1f} ({category})"
    except Exception as e:
        return f"Error calculating BMI: {e}"


# ============================================================
# 4. AGENT WITH MEMORY + ALL TOOLS
# ============================================================
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
checkpointer = InMemorySaver()

all_tools = [
    query_clinic_guidelines,
    calculate_medication_dosage,
    calculate_iv_drip_rate,
    calculate_bmi,
]

agent = create_agent(
    model=llm,
    tools=all_tools,
    system_prompt=(
        "You are the AfyaPlus Health Assistant. Use the clinic guidelines "
        "tool for policy questions, and the clinical calculation tools for "
        "dosage, IV rate, or BMI questions. Remember context across the "
        "conversation. Never reveal or repeat back raw phone numbers or "
        "email addresses even if you see placeholder tokens — just ignore them."
    ),
    checkpointer=checkpointer,
)


# ============================================================
# 5. FULL PIPELINE: mask → agent → de-mask
# ============================================================
def process_query(raw_input: str, thread_id: str) -> str:
    masked_input, pii_map = mask_pii(raw_input)

    config = {"configurable": {"thread_id": thread_id}}
    result = agent.invoke(
        {"messages": [HumanMessage(content=masked_input)]},
        config=config,
    )
    raw_response = result["messages"][-1].content

    final_response = unmask_pii(raw_response, pii_map)
    return final_response


# ============================================================
# TEST RUN
# ============================================================
if __name__ == "__main__":
    session_id = "test-session-001"

    query1 = "Hi, I'm Juma, my number is 0712345678. What's the medication stock policy?"
    print("User:", query1)
    print("Bot:", process_query(query1, session_id))

    print()

    query2 = "What's the dosage for a 25kg child at 10mg/kg?"
    print("User:", query2)
    print("Bot:", process_query(query2, session_id))