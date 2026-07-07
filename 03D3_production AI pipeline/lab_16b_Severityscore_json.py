# =============================================================================
# AFYAPLUS - Lab 13: Structured JSON Extraction
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
    "and keeps vomiting. We are in a village near Kilifi. Please help us quickly, "
    "the child is very weak."
)


# =============================================================================
# PART 1: BASIC STRUCTURED EXTRACTION (Lab 13 Main)
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


# =============================================================================
# PART 2: CHALLENGE - Add Severity Score (challenge13_severity.py)
# =============================================================================
print("=== PART 2: Challenge - Severity Score Extraction ===\n")

def extract_with_severity(sms_text):
    """
    Extended extraction with severity scoring (1-10).
    
    # SEVERITY SCORING ADDITION:
    # - Added "severity_score" field to JSON schema
    # - Added scoring rubric in system prompt (1-3 mild, 4-7 moderate, 8-10 severe)
    # - Post-processing: automatic alert when severity >= 8
    # - ALL changes in the prompt string - Python logic only consumes the result
    """
    
    # # UPDATED PROMPT: Now includes severity_score field + scoring guidance
    extraction_prompt = """
You are a backend administrative data extraction engine for AfyaPlus Health.
Analyse the following untrusted user SMS text. Return a valid JSON object
matching this schema:
{
  "patient_age_years": integer or null,
  "symptoms": ["string", "string"],
  "location_cluster": "string",
  "requires_emergency_dispatch": boolean,
  "severity_score": integer
}
SEVERITY SCORING RULES:
- Score 1-3: Mild symptoms (minor complaints, stable condition)
- Score 4-7: Moderate symptoms (concerning but not immediately life-threatening)
- Score 8-10: Severe symptoms (life-threatening, requires immediate intervention)
Base the score ONLY on the described symptoms and their urgency.
CRITICAL: Return ONLY raw JSON, no markdown formatting or conversational text.
"""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": extraction_prompt},
            {"role": "user", "content": f"SMS: {sms_text}"}
        ],
        temperature=0.0,
        response_format={"type": "json_object"}
    )
    
    parsed = json.loads(response.choices[0].message.content)
    return parsed


# # TEST CASE 1: Severe case (child with fever + vomiting + weakness)
print("--- Test 1: Severe Pediatric Case ---")
severe_case = (
    "Amani here. My 4-year-old child has had a hot body (fever) since yesterday "
    "and keeps vomiting. We are in a village near Kilifi. Please help us quickly, "
    "the child is very weak."
)
result1 = extract_with_severity(severe_case)
print(json.dumps(result1, indent=2))

# # AUTOMATED ALERT: High severity triggers immediate action
if result1.get("severity_score", 0) >= 8:
    print(f"\n🚨 HIGH SEVERITY ALERT (Score: {result1['severity_score']}/10)!")
    print(f"   Immediate dispatch to: {result1.get('location_cluster', 'Unknown')}")
    print(f"   Patient age: {result1.get('patient_age_years', 'Unknown')}")
    print(f"   Symptoms: {', '.join(result1.get('symptoms', []))}")
else:
    print(f"\n✅ Severity score {result1.get('severity_score')}/10 - Standard routing.")

print()

# # TEST CASE 2: Mild case (minor complaint)
print("--- Test 2: Mild Adult Case ---")
mild_case = "I have a small paper cut on my finger. I am in Mombasa town."
result2 = extract_with_severity(mild_case)
print(json.dumps(result2, indent=2))

if result2.get("severity_score", 0) >= 8:
    print(f"\n🚨 HIGH SEVERITY ALERT (Score: {result2['severity_score']}/10)!")
else:
    print(f"\n✅ Severity score {result2.get('severity_score')}/10 - Standard routing.")

print()

# # TEST CASE 3: Moderate case (concerning but not emergency)
print("--- Test 3: Moderate Adult Case ---")
moderate_case = (
    "I have had a bad cough and chest pain for 4 days. "
    "I am in the Nairobi area and can still walk and talk normally."
)
result3 = extract_with_severity(moderate_case)
print(json.dumps(result3, indent=2))

if result3.get("severity_score", 0) >= 8:
    print(f"\n🚨 HIGH SEVERITY ALERT (Score: {result3['severity_score']}/10)!")
else:
    print(f"\n✅ Severity score {result3.get('severity_score')}/10 - Standard routing.")


# =============================================================================
# KEY TAKEAWAYS & REFERENCE NOTES
# =============================================================================
# 
# 1. STRUCTURED JSON EXTRACTION PATTERN:
#    - System prompt defines exact JSON schema
#    - Forbid markdown wrappers (```json breaks json.loads)
#    - response_format={"type": "json_object"} for API-level enforcement
#    - temperature=0.0 for deterministic output
#    - json.loads() for parsing + validation
#
# 2. WHY JSON MODE IS SAFER THAN JUST ASKING:
#    - response_format={"type": "json_object"} GUARANTEES valid JSON at API level
#    - Just asking "return JSON" relies on model following instructions
#    - Without JSON mode, model might: wrap in markdown, add conversational text, 
#      return invalid JSON, or ignore the instruction entirely
#    - JSON mode = protocol-level guarantee, not just a polite request
#
# 3. PRODUCTION AUTOMATION WORKFLOW:
#    - SMS arrives → Extract structured JSON → Automated routing decision
#    - if severity >= 8: trigger emergency dispatch
#    - if requires_emergency_dispatch: alert medical team
#    - Structured data enables: database updates, dashboards, notifications
#
# 4. SEVERITY SCORING INTEGRATION:
#    - Added to JSON schema (no Python changes needed)
#    - Scoring rubric in prompt ensures consistent scoring
#    - Post-processing acts on score: >= 8 triggers alerts
#    - All logic in prompt + simple if/else in Python
#
# 5. COMMON PITFALLS:
#    - Markdown wrappers (```json) → json.loads fails → use "no markdown" rule
#    - Conversational text ("Sure! Here's your JSON:") → parse failure
#    - Missing fields → use .get() with defaults in Python
#    - temperature > 0 → inconsistent field names → use 0.0 for extraction
# =============================================================================