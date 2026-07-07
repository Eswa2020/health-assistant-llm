# =============================================================================
# AFYAPLUS - Lab 16: Structured JSON Extraction
# =============================================================================
# CONCEPT: Production backends need machine-parseable data (JSON), not free text.
# Structured extraction forces the model to return a specific JSON schema that
# downstream code can parse reliably for automated workflows like SMS dispatch,
# database updates, or routing decisions.
# =============================================================================

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

# # RAW SMS INPUT: Unstructured, messy, real-world patient text
# # This is what actually arrives via SMS - no forms, no structure
raw_patient_sms = (
    "Amani here. My 4-year-old child has had a hot body (fever) since yesterday "
    " We are in a village near kakamega. Please help us quickly, "
    "the child is not responsive."
)


# =============================================================================
# PART 1: BASIC STRUCTURED EXTRACTION 
# =============================================================================
print("=== PART 1: Structured JSON Extraction ===\n")

def extract_structured_patient_data(sms_text):
    """
    Extracts structured JSON from unstructured SMS text.
    
    # STRUCTURED OUTPUT PATTERN:
    # 1. System prompt defines exact JSON schema
    # 2. Forbids markdown wrappers (```json fences break json.loads)
    # 3. response_format={"type": "json_object"} enforces JSON at API level
    # 4. temperature=0.0 ensures deterministic field population
    # 5. json.loads() validates and converts to Python dict
    """
    
    # ---- ALL PROMPT ENGINEERING LIVES HERE ----
    extraction_prompt = """
You are a backend administrative data extraction engine for AfyaPlus Health.
Analyse the following untrusted user SMS text. Extract the required parameters
into a valid JSON object matching this schema:
{
  "patient_age_years": integer or null,
  "symptoms": ["string", "string"],
  "location_cluster": "string",
  "requires_emergency_dispatch": boolean
}
CRITICAL: Do not include any markdown formatting (no triple-backtick json fences)
or any conversational text. Return ONLY the raw JSON string.
"""
    # # KEY: "Return ONLY raw JSON" + no markdown = clean parseable output
    # # If model wraps in ```json, json.loads() will fail
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": extraction_prompt},
            {"role": "user", "content": f"SMS: {sms_text}"}
        ],
        temperature=0.0,  # # Deterministic: same input = same JSON structure
        response_format={"type": "json_object"}  # # API-level JSON guarantee
    )
    
    # # Parse JSON string → Python dictionary for downstream code
    parsed = json.loads(response.choices[0].message.content)
    return parsed


# # TEST: Basic structured extraction
parsed = extract_structured_patient_data(raw_patient_sms)
print("--- Automated API Extraction Complete ---")
print(json.dumps(parsed, indent=2))

# # AUTOMATED DECISION-MAKING: Code acts on structured data
# # This is why we need JSON - code can't reliably parse paragraphs
if parsed.get("requires_emergency_dispatch"):
    print(f"\n🚨 ALERT: Dispatching emergency SMS to {parsed['location_cluster']} "
          f"medical team for a patient aged {parsed['patient_age_years']}.")
else:
    print("\n✅ System Status: Staging ticket in standard queue.")

print("\n" + "="*60 + "\n")

