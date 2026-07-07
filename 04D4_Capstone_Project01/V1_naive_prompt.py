# =============================================================================
# AFYAPLUS PROMPT EVOLUTION - Version 1: Naive Zero-Shot
# =============================================================================
# This is what NOT to do in production.
# No role, no structure, no JSON mode – just a bare instruction.
# Expected failure: conversational fluff, no parseable output.
# =============================================================================

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

patient_message = (
    "Hello AfyaPlus, I am Chidinma. I am 7 months pregnant. "
    "For the past two days I have had a severe headache and my feet are swollen. "
    "I feel safe waiting for my appointment next week."
)

# ---- NAIVE PROMPT: Just a simple instruction ----
prompt = f"""
Analyse this patient message and tell me what to do: "{patient_message}"
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.0,
    max_tokens=300
)

print("=== VERSION 1 OUTPUT (NAIVE) ===")
print(response.choices[0].message.content)
print("\n❌ Problems: conversational, no structure, might agree with patient's false sense of safety.")