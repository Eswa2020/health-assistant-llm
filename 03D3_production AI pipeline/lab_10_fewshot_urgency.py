# =============================================================================
# AFYAPLUS - Lab 10: Few-Shot Patient Urgency Classifier
# =============================================================================
# CONCEPT: Few-shot prompting dramatically improves output reliability by
# showing the model exact examples of the expected input-output format.
# The model "learns" from these examples within the conversation context
# and replicates the pattern for new inputs.
# =============================================================================

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

# =============================================================================
# MAIN LAB FUNCTION: Few-Shot Patient Urgency Classifier
# =============================================================================
def analyse_patient_urgency_few_shot(new_patient_query):
    """
    Classifies patient queries using few-shot prompting.
    
    # KEY INSIGHT: All prompt engineering happens in the messages list.
    # The system message defines the task, alternating user-assistant pairs
    # demonstrate the exact output format we want, and the final user message
    # is the live target the model will classify.
    
    # WHY FEW-SHOT?: Zero-shot prompts often return verbose responses or
    # invent new categories. Few-shot examples act as a "format anchor" -
    # the model sees exactly what we want and replicates the pattern.
    
    # WHY temperature=0.0?: Forces deterministic behavior. The model always
    # picks the most likely token, preventing creative and wrong outputs
    # like "I think this might be CRITICAL" instead of just "CRITICAL".
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.0,  # # DETERMINISTIC: Always picks most likely output
        messages=[
            # ---- ROLE & TASK ----
            # # System message: Sets the global behavior and rules
            {"role": "system",
             "content": "Classify incoming user medical queries into exactly "
                        "one category: CRITICAL, NON_URGENT, or ROUTINE. "
                        "Respond with ONLY 'Category: <LABEL>' and nothing else."},
            
            # ---- FEW-SHOT EXAMPLE 1: a CRITICAL case ----
            # # EXAMPLE PAIR: Shows model what a CRITICAL query looks like
            # # The user message contains the query, assistant responds with format
            {"role": "user",
             "content": "Query: I cannot breathe and my left arm feels numb."},
            {"role": "assistant",
             "content": "Category: CRITICAL"},
            
            # ---- FEW-SHOT EXAMPLE 2: a ROUTINE case ----
            # # SECOND EXAMPLE: Demonstrates another category to prevent bias
            # # Without this, the model might default everything to CRITICAL
            {"role": "user",
             "content": "Query: I need to renew my allergy pills prescription "
                        "next month."},
            {"role": "assistant",
             "content": "Category: ROUTINE"},
            
            # ---- LIVE TARGET QUERY ----
            # # LIVE INPUT: Placed after examples so model follows established pattern
            # # The model sees this as "just another query to classify" in the conversation
            {"role": "user",
             "content": f"Query: {new_patient_query}"}
        ]
    )
    return response.choices[0].message.content


# =============================================================================
# TEST THE BASIC LAB CLASSIFIER
# =============================================================================
verdict = analyse_patient_urgency_few_shot(
    "My child has a mild fever but is laughing and playing.")
print(verdict)  


# =============================================================================
# CHALLENGE: Add a Fourth Category (EMERGENCY_DISPATCH)
# =============================================================================
def classify_with_emergency(new_patient_query):
    """
    Extended classifier with EMERGENCY_DISPATCH category for ambulance cases.
    
    # CHALLENGE SOLUTION: Adding a fourth category requires:
    # 1. Updating the system message to list all four categories
    # 2. Adding at least one example pair for the new category
    # 3. Testing with both edge cases and clear-cut examples
    
    # WHY ADD EXAMPLES?: Without an example, the model might never use
    # EMERGENCY_DISPATCH because it hasn't seen what qualifies. Examples
    # define the boundary between CRITICAL (hospital needed) and 
    # EMERGENCY_DISPATCH (ambulance/immediate life-saving intervention).
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.0,
        messages=[
            # ---- UPDATED SYSTEM MESSAGE ----
            # # CRITICAL UPDATE: Now listing all FOUR categories explicitly
            # # The model needs to know EMERGENCY_DISPATCH exists as an option
            {"role": "system",
             "content": "Classify incoming user medical queries into exactly "
                        "one category: CRITICAL, NON_URGENT, ROUTINE, or "
                        "EMERGENCY_DISPATCH. Respond with ONLY 'Category: "
                        "<LABEL>' and nothing else. Use EMERGENCY_DISPATCH for "
                        "life-threatening situations requiring immediate "
                        "ambulance dispatch."},
            
            # ---- EXISTING EXAMPLES (unchanged) ----
            {"role": "user",
             "content": "Query: I cannot breathe and my left arm feels numb."},
            {"role": "assistant",
             "content": "Category: CRITICAL"},
            
            {"role": "user",
             "content": "Query: I need to renew my allergy pills next month."},
            {"role": "assistant",
             "content": "Category: ROUTINE"},
            
            # ---- NEW EMERGENCY_DISPATCH EXAMPLE ----
            # # CRITICAL ADDITION: Shows model what qualifies for ambulance dispatch
            # # Uncontrolled severe bleeding = immediate life threat = EMERGENCY_DISPATCH
            # # This example teaches the boundary: worse than CRITICAL, needs ambulance
            {"role": "user",
             "content": "Query: Car accident victim with severe head injury, "
                        "unconscious and not breathing normally."},
            {"role": "assistant",
             "content": "Category: EMERGENCY_DISPATCH"},
            
            # ---- LIVE TARGET QUERY ----
            # # Same pattern: append live query after all examples
            {"role": "user",
             "content": f"Query: {new_patient_query}"}
        ]
    )
    return response.choices[0].message.content


# =============================================================================
# TEST THE CHALLENGE CLASSIFIER
# =============================================================================
# # TEST CASE 1: Minor injury should be NON_URGENT
# # The model should recognize this doesn't need hospital or ambulance
print("\n--- Challenge Tests ---")
print("Test 1 - Minor injury:")
print(classify_with_emergency("I have a small bruise on my knee"))


# # TEST CASE 2: Severe bleeding should be EMERGENCY_DISPATCH
# # This is exactly why we added the category - uncontrolled bleeding = ambulance
print("\nTest 2 - Severe bleeding:")
print(classify_with_emergency(
    "Severe bleeding that will not stop after 20 minutes"))


# # BONUS TEST: Verify CRITICAL still works with new system
# # Edge case: needs hospital but not necessarily ambulance
print("\nTest 3 - Verify CRITICAL still works:")
print(classify_with_emergency(
    "My 7year old has a  high fever 37.5 celcius and is very drowsy,but can still respond"))



# =============================================================================
# KEY TAKEAWAYS & REFERENCE NOTES
# =============================================================================
# 
# 1. FEW-SHOT PROMPTING PATTERN:
#    - System message defines task + output format
#    - 2-3 alternating user/assistant example pairs
#    - Live query appended at the end
#    - temperature=0.0 for deterministic output
#
# 2. WHY THIS WORKS:
#    - Models are trained on conversation patterns
#    - Examples serve as "in-context learning"
#    - The model treats the live query as continuation of the pattern
#    - Eliminates ambiguity about format and categories
#
# 3. ADDING NEW CATEGORIES:
#    - Always update system message first
#    - Add at least one clear example of the new category
#    - Test boundary cases to ensure proper classification
#    - Consider adding counter-examples if needed
#
# 4. PRODUCTION CONSIDERATIONS:
#    - Few-shot examples are part of your prompt engineering, not model training
#    - Examples are sent with EVERY API call (increases token usage)
#    - Choose diverse examples that cover your expected use cases
#    - Monitor for categories the model never/always picks (bias detection)
# =============================================================================