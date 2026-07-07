# =============================================================================
# AFYAPLUS - Lab 9: Three-Version Prompt Iteration
# =============================================================================
# CONCEPT: Iterative prompt refinement tests the same input against progressively
# improved prompts. Start naive → constrain format → add CoT + guardrails.
# The Python skeleton stays identical; only the prompt string changes.
# This is prompt engineering as the unit of work.
# =============================================================================

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

# # TEST CASE: Preeclampsia red flags in third trimester
# # Severe headache + sudden swelling = classic preeclampsia indicators
# # Patient says "safe to wait" but clinical reality says EMERGENCY
patient_case = (
    "Hello AfyaPlus, I am Chidinma. I am 7 months pregnant with my third child. "
    "For the past two days, I have had a severe headache that will not go away and "
    "my feet are suddenly very swollen. I feel safe waiting for my appointment next week."
)

# =============================================================================
# PROMPT V1: NAIVE (zero-shot, no structure)
# =============================================================================
# # FLAWS: Open-ended question invites conversational response.
# # Model may agree with patient's "feel safe" assumption.
# # Output is a paragraph - cannot be parsed by downstream automation.
# # No clinical context provided - model lacks obstetric triage framing.
prompt_v1 = f"""
Look at this message from a patient and tell me if it is dangerous: "{patient_case}"
"""

# =============================================================================
# PROMPT V2: ROLE + DIRECT INSTRUCTION + OUTPUT TEMPLATE
# =============================================================================
# # IMPROVEMENTS: Role sets obstetric expertise, template forces parseable output.
# # STILL MISSING: No reasoning requirement - model might skip preeclampsia link.
# # Output is structured (key-value) but reasoning is invisible/unauditable.
prompt_v2 = f"""
You are an expert obstetric triage nurse at AfyaPlus Health. Analyse the patient
message for life-threatening third-trimester complications, specifically signs of
high blood pressure, preeclampsia (severe headaches, vision changes, sudden
swelling), or bleeding.

Provide your output exactly like this:
RISK LEVEL: [CRITICAL / NORMAL]
ACTION REQUIRED: [IMMEDIATE OUTREACH / STANDARD FOLLOWUP]
SUMMARY: [1-sentence explanation]

Patient Message: "{patient_case}"
"""

# =============================================================================
# PROMPT V3: ROLE + CoT REASONING + DEFENSIVE GUARDRAILS
# =============================================================================
# # WHY THIS WORKS: CoT forces enumeration of preeclampsia markers BEFORE deciding.
# # Guardrails prevent diagnosis/prescription (legal safety).
# # "Defensive, automated triage routing system" role removes bedside manner.
# # Step-by-step thought process creates audit trail for clinical review.
# # Temperature=0.0 ensures deterministic critical-flag detection.
prompt_v3 = f"""
You are a defensive, automated triage routing system for AfyaPlus Health. Your
role is to categorise patient intake text to flag high-risk pregnancy complications.

CRITICAL INSTRUCTIONS:
1. Analyse the text step-by-step for high-risk flags: preeclampsia markers
   (persistent headache + peripheral edema), premature labour, or fluid loss.
2. Do NOT offer a medical diagnosis. Do NOT prescribe medications.
3. Keep tone completely objective. No conversational openings.

Use this exact output format:
THOUGHT PROCESS:
- [Step-by-step clinical evaluation of symptoms]
FINAL STATUS: [CRITICAL_URGENT / ROUTINE_CARE]
ROUTING DESTINATION: [Emergency Medical Call Team / General Queue]

Patient Message: "{patient_case}"
"""

# =============================================================================
# SINGLE PYTHON LOOP DRIVES ALL THREE ITERATIONS
# =============================================================================
# # KEY INSIGHT: The API call is identical across all three versions.
# # Only the prompt string changes. This proves prompt engineering
# # is the unit of work - the Python is just plumbing.
prompts = [prompt_v1, prompt_v2, prompt_v3]
for index, current_prompt in enumerate(prompts, 1):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": current_prompt}],
        temperature=0.0  # # Deterministic for consistent comparison across versions
    )
    print(f"====== PROMPT VERSION {index} OUTPUT ======")
    print(response.choices[0].message.content)
    print()


# =============================================================================
# CHALLENGE: Build the Comparison Matrix (in comparison.md file)
# =============================================================================
print("""
# =============================================================================
# COMPARISON MATRIX 
# =============================================================================

| Evaluation Metric                      | V1 (Naive)           | V2 (Constrained)       | V3 (Defensive CoT)        |
|----------------------------------------|----------------------|------------------------|---------------------------|
| Output Type (paragraph vs key-value)   | Paragraph            | Key-Value pairs        | Structured sections       |
| Preeclampsia Detection (flagged?)      | May miss or agree    | Usually flags          | Always flags + explains   |
| Automation Readiness (regex-parseable) | No (free text)       | Yes (parseable labels) | Yes (parseable + audit)   |
| Conversational Fluff (Yes/No)          | Yes                  | Minimal                | No (completely objective) |

## Reflection
V3 prevents the model from agreeing with Chidinma's assumption to wait because
the Chain-of-Thought instruction forces the model to enumerate clinical markers
(severe persistent headache + sudden peripheral edema in third trimester) BEFORE
reaching a conclusion. When the model lists these preeclampsia red flags in its
thought process, the logical conclusion becomes inescapable: this is CRITICAL_URGENT
requiring immediate outreach, regardless of the patient's subjective feeling they are ok.
The defensive guardrails ("Do NOT offer a medical diagnosis") and objective tone
further prevent the model from softening its output with reassuring conversational
language that might downplay the emergency.
""")


# =============================================================================
# KEY TAKEAWAYS & REFERENCE NOTES
# =============================================================================
# 
# 1. ITERATIVE REFINEMENT PATTERN:
#    - V1 (Naive): Test baseline, identify failures
#    - V2 (Constrained): Add role + output template
#    - V3 (Defensive CoT): Add reasoning + guardrails
#    - Change ONE thing at a time to isolate what worked
#
# 2. WHY V3 WINS (Defensive CoT):
#    - CoT forces clinical marker enumeration before decision
#    - Guardrails prevent diagnosis/prescription (legal safety)
#    - "Defensive routing system" role removes bedside softness
#    - Structured output enables automated downstream routing
#    - Audit trail for clinical review and compliance
#
# 3. PROMPT ENGINEERING DISCIPLINE:
#    - Same API call, same input, same temperature
#    - Only the prompt string changes between versions
#    - Measure: parseability, accuracy, safety, audit trail
#    - Document each version's effect (capstone README evidence)
#
# 4. PRODUCTION CONSIDERATIONS:
#    - High-stakes medical systems MUST use CoT + guardrails
#    - Patient "feels safe" ≠ clinically safe (model must override)
#    - Parseable output enables automated routing pipelines
#    - Defensive prompts prevent dangerous agreement with patients
# =============================================================================