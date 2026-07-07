# =============================================================================
# AFYAPLUS TRIAGE ENGINE - Week 1 Capstone Project
# =============================================================================
# Combines: Cloud API (GPT-4o-mini), Local Ollama fallback, Role-Based + CoT
# prompting, Defensive guardrails, Native JSON mode, Error handling with
# timeouts, and Automatic cloud-to-local failover.
# =============================================================================

import os
import json
import time
import sys
import httpx
from datetime import datetime, timezone
from dotenv import load_dotenv
from openai import OpenAI, APITimeoutError, APIError, APIConnectionError

# Load environment variables
load_dotenv()

# =============================================================================
# PHASE 1: ARCHITECTURAL FOUNDATION - Dual Pathway Setup
# =============================================================================

# Cloud pathway: GPT-4o-mini via OpenAI
cloud_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=4.0  # # PHASE 2: Strict 4-second timeout
)

# Edge pathway: Local Ollama instance
ollama_client = OpenAI(
    base_url="http://localhost:11434/v1",  # # Default Ollama endpoint
    api_key="ollama",  # # Placeholder - Ollama ignores this
   timeout=httpx.Timeout(40.0, connect=10.0)  # total 40s, connect 10s
)

# =============================================================================
# PHASE 3: ADVANCED PROMPT STRUCTURAL ENGINEERING
# =============================================================================



def build_defensive_cot_prompt(patient_message):
    """
    Builds the production-grade prompt with three layers:
    1. Role-based assignment: Defines operational identity
    2. Chain-of-Thought: Forces step-by-step reasoning
    3. Defensive guardrails: Prevents fluff, hallucinations, diagnoses
    """
    
    SYSTEM_PROMPT = """
You are a strict, defensive automated triage routing engine for AfyaPlus Health,
a medical triage platform serving rural communities in Kenya.

ROLE DEFINITION:
- You are a BACKEND PROCESSING ENGINE, not a conversational assistant
- Your ONLY function is to analyse symptoms and produce structured triage output
- You have NO bedside manner - clinical precision over conversation

CHAIN-OF-THOUGHT REASONING REQUIREMENT:
Before producing your final output, you MUST reason through:
1. SYMPTOM IDENTIFICATION: List each symptom mentioned and its clinical significance
2. RISK ASSESSMENT: Evaluate if symptoms indicate life-threatening conditions
3. ROUTING LOGIC: Determine the appropriate care pathway based on assessment

DEFENSIVE GUARDRAILS (ABSOLUTE RULES):
- NEVER diagnose: Do not state "the patient has [condition]"
- NEVER prescribe: Do not mention specific medications or dosages
- NEVER converse: No "Hello!", "I understand", "I'm sorry", or any conversational text
- NEVER calculate: Do not compute BMI, drug doses, or any clinical calculations
- NEVER speculate beyond symptoms: Stick strictly to what is described
- NEVER use markdown: No ```json fences, no bold, no italics
- ALWAYS recommend professional care for serious symptoms
- ALWAYS flag pregnancy-related symptoms as high priority
- ALWAYS consider rural context: Distance to care matters

OUTPUT FORMAT:
Return ONLY a valid JSON object matching this exact schema.
No text before or after the JSON.
"""
    
    USER_PROMPT = f"""
PATIENT MESSAGE TO TRIAGE:
{patient_message}

Analyse this message following your chain-of-thought process.
Return ONLY the JSON object as specified.
"""
    
    return SYSTEM_PROMPT, USER_PROMPT


# =============================================================================
# PHASE 4: NATIVE JSON OUTPUT SCHEMA ENFORCEMENT
# =============================================================================

# # AFYAPLUS TRIAGE SCHEMA
TRIAGE_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "afyaplus_triage_output",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "is_critical_emergency": {
                    "type": "boolean",
                    "description": "Whether immediate medical intervention is required"
                },
                "detected_symptoms": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of symptoms mentioned by the patient"
                },
                "clinical_reasoning_summary": {
                    "type": "string",
                    "description": "Brief step-by-step clinical reasoning"
                },
                "routing_destination": {
                    "type": "string",
                    "enum": [
                        "EMERGENCY_DISPATCH",
                        "URGENT_CARE_CLINIC",
                        "STANDARD_APPOINTMENT",
                        "SELF_CARE_GUIDANCE"
                    ],
                    "description": "Where the patient should be routed"
                },
                "severity_score": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10,
                    "description": "Severity score 1 (minor) to 10 (life-threatening)"
                },
                "requires_ambulance": {
                    "type": "boolean",
                    "description": "Whether ambulance dispatch is needed (rural context)"
                }
            },
            "required": [
                "is_critical_emergency",
                "detected_symptoms",
                "clinical_reasoning_summary",
                "routing_destination",
                "severity_score",
                "requires_ambulance"
            ],
            "additionalProperties": False
        }
    }
}


# =============================================================================
# PHASE 2 & 5: RESILIENCE DESIGN & END-TO-END EXECUTION
# =============================================================================

def call_cloud_api(system_prompt, user_prompt):
    """
    Attempt cloud inference with timeout and error handling.
    Returns (success, result_dict_or_error_message, latency, pathway_used)
    """
    start_time = time.time()
    
    try:
        response = cloud_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,
            max_tokens=500,
            response_format=TRIAGE_SCHEMA  # # Native JSON mode
        )
        
        latency = time.time() - start_time
        result = json.loads(response.choices[0].message.content)
        return True, result, latency, "CLOUD (GPT-4o-mini)"
        
    except APITimeoutError:
        latency = time.time() - start_time
        return False, f"Cloud timeout after {latency:.1f}s", latency, None
        
    except APIConnectionError:
        latency = time.time() - start_time
        return False, f"Cloud connection failed after {latency:.1f}s", latency, None
        
    except APIError as e:
        latency = time.time() - start_time
        return False, f"Cloud API error: {str(e)[:100]}", latency, None
        
    except json.JSONDecodeError as e:
        latency = time.time() - start_time
        return False, f"Cloud returned invalid JSON: {str(e)[:100]}", latency, None
        
    except Exception as e:
        latency = time.time() - start_time
        return False, f"Unexpected cloud error: {str(e)[:100]}", latency, None


def call_ollama_fallback(system_prompt, user_prompt):
    """
    Fallback to local Ollama when cloud fails.
    Returns (success, result_dict_or_error_message, latency, pathway_used)
    """
    start_time = time.time()
    
    try:
        response = ollama_client.chat.completions.create(
            model="llama3.2",  # # Lightweight local model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,
            max_tokens=500,
            response_format={"type": "json_object"}  # # Fallback JSON mode
        )
        
        latency = time.time() - start_time
        result = json.loads(response.choices[0].message.content)
        return True, result, latency, "LOCAL (Ollama/Llama3.2)"
        
    except json.JSONDecodeError as e:
        latency = time.time() - start_time
        return False, f"Local model returned invalid JSON: {str(e)[:100]}", latency, None
        
    except Exception as e:
        latency = time.time() - start_time
        return False, f"Local model error: {str(e)[:100]}", latency, None


def process_patient(patient_message, force_fallback=False):
    """
    Main processing pipeline:
    1. Try cloud pathway first
    2. Fall back to local Ollama if cloud fails
    3. Return structured result with metadata
    """
    
    # Build the defensive CoT prompt
    system_prompt, user_prompt = build_defensive_cot_prompt(patient_message)
    
    result = None
    pathway_used = None
    cloud_latency = None
    local_latency = None
    fallback_triggered = False
    
    # Phase 5: Try cloud first, fall back to local
    if not force_fallback:
        print(" Attempting cloud inference (GPT-4o-mini)...")
        success, result, cloud_latency, pathway_used = call_cloud_api(system_prompt, user_prompt)
        
        if success:
            print(f"   ✅ Cloud success ({cloud_latency:.2f}s)")
        else:
            print(f"   ❌ Cloud failed: {result}")
            print("🔄 Falling back to local Ollama...")
            fallback_triggered = True
    
    # Fallback to local if cloud failed or force_fallback is True
    if force_fallback or not success if not force_fallback else True:
        if force_fallback:
            print(" Forcing local Ollama pathway (testing fallback)...")
        
        success, result, local_latency, pathway_used = call_ollama_fallback(system_prompt, user_prompt)
        
        if success:
            print(f"   ✅ Local success ({local_latency:.2f}s)")
        else:
            print(f"   ❌ Local also failed: {result}")
            # Ultimate fallback - return safe default
            result = {
                "is_critical_emergency": True,
                "detected_symptoms": ["UNKNOWN - SYSTEM ERROR"],
                "clinical_reasoning_summary": "Both cloud and local inference failed. Patient requires human evaluation.",
                "routing_destination": "EMERGENCY_DISPATCH",
                "severity_score": 10,
                "requires_ambulance": True
            }
            pathway_used = "FALLBACK (Hardcoded Safe Default)"
    
    return {
        "result": result,
        "pathway_used": pathway_used,
        "cloud_latency": cloud_latency,
        "local_latency": local_latency,
        "fallback_triggered": fallback_triggered,
        "timestamp": datetime.now(timezone.utc).isoformat(),  # Fixed: timezone.utc instead of datetime.UTC
        "patient_message": patient_message
    }


# =============================================================================
# PHASE 5: END-TO-END DEMONSTRATION
# =============================================================================

def print_triage_result(processing_result):
    """Pretty-print the triage result with routing decision."""
    
    result = processing_result["result"]
    
    print("\n" + "=" * 60)
    print(" AFYAPLUS TRIAGE ENGINE - RESULT")
    print("=" * 60)
    
    # Print the parsed JSON
    print("\n Structured Triage Output:")
    print(json.dumps(result, indent=2))
    
    # Print routing decision
    print("\n" + "-" * 40)
    print(" ROUTING DECISION:")
    
    is_critical = result.get("is_critical_emergency", False)
    severity = result.get("severity_score", 5)
    routing = result.get("routing_destination", "UNKNOWN")
    needs_ambulance = result.get("requires_ambulance", False)
    
    if is_critical or severity >= 8:
        print(f"🔴 CRITICAL PRIORITY - {routing}")
        if needs_ambulance:
            print("   🚑 AMBULANCE DISPATCH REQUIRED")
        print("    Immediate medical attention needed!")
    elif severity >= 5:
        print(f"🟡 MODERATE PRIORITY - {routing}")
        print("    Schedule appointment within 24-48 hours")
    else:
        print(f"🟢 STANDARD PRIORITY - {routing}")
        print("    Routine care pathway")
    
    # Print metadata
    print(f"\n Processing Metadata:")
    print(f"   Pathway Used: {processing_result['pathway_used']}")
    print(f"   Fallback Triggered: {processing_result['fallback_triggered']}")
    if processing_result['cloud_latency']:
        print(f"   Cloud Latency: {processing_result['cloud_latency']:.2f}s")
    if processing_result['local_latency']:
        print(f"   Local Latency: {processing_result['local_latency']:.2f}s")
    print(f"   Timestamp: {processing_result['timestamp']}")
    print("=" * 60 + "\n")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" AFYAPLUS TRIAGE ENGINE - Week 1 Capstone")
    print("=" * 60)
    print(f"Start time: {datetime.now(timezone.utc).isoformat()}")  # Fixed: timezone.utc
    print()
    
    # Test cases covering different scenarios
    test_cases = [
        {
            "name": "TEST 1: Preeclampsia Emergency (should be CRITICAL)",
            "message": (
                "Hello AfyaPlus, I am Chidinma. I am 7 months pregnant with my third child. "
                "For the past two days, I have had a severe headache that will not go away and "
                "my feet are suddenly very swollen. I feel safe waiting for my appointment next week."
            ),
            "force_fallback": False
        },
        {
            "name": "TEST 2: Minor Complaint (should be STANDARD)",
            "message": "I have a small bruise on my knee from playing football. It doesn't hurt much.",
            "force_fallback": False
        },
        {
            "name": "TEST 3: FORCED FALLBACK - Testing Local Ollama",
            "message": "My child has a fever of 39°C and is very tired. We are in a village near Kilifi.",
            "force_fallback": True  # # Force local to demonstrate fallback
        }
    ]
    
    # Process each test case
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"{test_case['name']}")
        print(f"{'='*60}")
        print(f"Patient Message: \"{test_case['message'][:100]}...\"")
        
        processing_result = process_patient(
            patient_message=test_case["message"],
            force_fallback=test_case.get("force_fallback", False)
        )
        
        print_triage_result(processing_result)
        
        # Small delay between tests
        if i < len(test_cases):
            time.sleep(2)
    
    print("\n Capstone demonstration complete!")
    print("   Check README.md for documentation and analysis.")