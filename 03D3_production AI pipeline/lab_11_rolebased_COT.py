# =============================================================================
# AFYAPLUS - Lab 11: Role-Based & Chain-of-Thought Triage Reasoning
# =============================================================================
# CONCEPT: Role-based prompting assigns a professional persona (e.g., triage nurse)
# to constrain behaviour. Chain-of-Thought (CoT) forces step-by-step reasoning
# BEFORE the final answer, reducing hallucinations by allocating "thinking time".
# The system message contains ALL prompt engineering; the Python is just API plumbing.
# =============================================================================

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

# =============================================================================
# MAIN LAB: Triage Reasoning with Role + Chain-of-Thought
# =============================================================================
def run_triage_reasoning(symptom_report):
    """
    Forces the model to reason step-by-step before giving a directive.
    
    # WHY ROLE?: "Expert emergency triage nurse" sets medical context,
    # safety-conscious tone, and appropriate expertise level.
    # WHY CoT?: Without step-by-step reasoning, the model guesses the final
    # answer on the first token - high hallucination risk. Forcing intermediate
    # steps creates an audit trail and improves accuracy on complex cases.
    # WHY TEMPLATE?: The structural layout (REASONING STEPS → FINAL DIRECTIVE)
    # ensures reasoning happens BEFORE the conclusion, not after.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,  # # Low temp for consistency, slight variation for natural reasoning
        messages=[
            {
                "role": "system",
                "content": (
                    # # ROLE: Assigns professional persona and expertise baseline
                    "You are an expert emergency triage nurse at AfyaPlus Health. "
                    # # CoT INSTRUCTION: Forces reasoning before conclusion
                    "Analyse the user symptoms. You MUST explain your clinical "
                    "reasoning step-by-step BEFORE concluding with a final directive. "
                    # # OUTPUT TEMPLATE: Locks structural layout for parsing
                    "Follow this EXACT structural layout:\n\n"
                    "REASONING STEPS:\n"
                    "- [Step 1]\n"
                    "- [Step 2]\n"
                    "FINAL DIRECTIVE: [Emergency Room / Clinic Appointment / Home Care]"
                )
            },
            {"role": "user", "content": symptom_report}
        ]
    )
    return response.choices[0].message.content

# # TEST CASE: Delayed symptoms after head injury - needs reasoning, not just label
complex_case = (
    "I bumped my head an hour ago. I felt fine at first, "
    "but now I am getting dizzy and nauseous."
)
print("=== Lab 11: Role + CoT Triage ===")
print(run_triage_reasoning(complex_case))


# =============================================================================
# CHALLENGE: Add Confidence Score (HIGH/MEDIUM/LOW)
# =============================================================================
def run_triage_with_confidence(symptom_report):
    """
    Extended version with confidence scoring.
    
    # CHALLENGE SOLUTION: Added CONFIDENCE field to output template.
    # Model must justify confidence based on reasoning completeness.
    # LOW confidence when information is missing (key safety feature).
    # ALL changes are in the system message string - no Python changes needed.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert emergency triage nurse at AfyaPlus Health. "
                    "Analyse the user symptoms. You MUST explain your clinical "
                    "reasoning step-by-step BEFORE concluding with a final directive. "
                    "Follow this EXACT structural layout:\n\n"
                    "REASONING STEPS:\n"
                    "- [Step 1]\n"
                    "- [Step 2]\n"
                    "FINAL DIRECTIVE: [Emergency Room / Clinic Appointment / Home Care]\n"
                    # # CONFIDENCE SCORE: Added to output template
                    "CONFIDENCE: [HIGH/MEDIUM/LOW]\n\n"
                    # # CONFIDENCE RULE: Forces LOW when info is incomplete
                    # # This prevents overconfident recommendations on vague symptoms
                    "Use LOW confidence whenever the reasoning steps indicate "
                    "missing critical information (vital signs, duration, severity, "
                    "or patient history). Use HIGH only when symptoms clearly "
                    "match a specific pathway with no ambiguity."
                )
            },
            {"role": "user", "content": symptom_report}
        ]
    )
    return response.choices[0].message.content


# =============================================================================
# TEST THE CHALLENGE CLASSIFIER
# =============================================================================
print("\n=== Challenge 11: Confidence Scores ===")

# # TEST 1: Clear case with detailed symptoms → Expect HIGH confidence
# # Head injury + specific delayed symptoms = clear Emergency Room directive
print("\n--- Clear Case (expect HIGH confidence) ---")
print(run_triage_with_confidence(
    "I bumped my head an hour ago. I felt fine at first, "
    "but now I am getting dizzy and nauseous."
))

# # TEST 2: Vague case with minimal info → Expect LOW confidence
# # "Not feeling well" could be anything - model should flag uncertainty
print("\n--- Vague Case (expect LOW confidence) ---")
print(run_triage_with_confidence(
    "I don't feel well."
))

# # TEST 3: Moderate case → Expect MEDIUM confidence
# # Clear symptom but missing key details (how high is the fever?)
print("\n--- Moderate Case (expect MEDIUM confidence) ---")
print(run_triage_with_confidence(
    "I have had a fever for two days and a sore throat."
))


# =============================================================================
# KEY TAKEAWAYS & REFERENCE NOTES
# =============================================================================
# 
# 1. ROLE-BASED PROMPTING:
#    - Persona: "expert emergency triage nurse" sets medical context
#    - Constrains tone, terminology, and decision boundaries
#    - All in system message - no Python changes needed
#
# 2. CHAIN-OF-THOUGHT (CoT):
#    - Forces reasoning BEFORE conclusion (not after)
#    - Reduces hallucinations by allocating "thinking time"
#    - Creates audit trail for clinical review
#    - Template layout enforces reasoning-before-decision order
#
# 3. CONFIDENCE SCORES:
#    - LOW when critical info missing (safety feature)
#    - HIGH only when symptoms clearly match a pathway
#    - Justified by reasoning completeness, not guesswork
#
# 4. PRODUCTION VALUE:
#    - Auditable AI decisions (clinicians can review reasoning)
#    - Confidence flags allow human escalation workflows
#    - Template parsing enables automated downstream routing
#    - Same API skeleton as Labs 5 & 7 - only system message changes
# =============================================================================