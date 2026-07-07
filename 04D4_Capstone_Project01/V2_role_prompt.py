# =============================================================================
# AFYAPLUS PROMPT EVOLUTION - Version 2: Role + Output Template
# =============================================================================
# Improvement: Adds a clinical role and a structured output format.

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

# ---- ROLE-BASED PROMPT WITH OUTPUT TEMPLATE ----
SYSTEM_PROMPT = """
You are an obstetric triage nurse at AfyaPlus Health.
Analyse the patient message and provide your output exactly like this:

RISK LEVEL: [CRITICAL / NORMAL]
ACTION REQUIRED: [IMMEDIATE OUTREACH / STANDARD FOLLOWUP]
SUMMARY: [1-sentence explanation]
"""

USER_PROMPT = f"Patient Message: {patient_message}"

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT}
    ],
    temperature=0.0,
    max_tokens=300
)

print("=== VERSION 2 OUTPUT (ROLE + TEMPLATE) ===")
print(response.choices[0].message.content)
print("\n⚠️  Better, but still risks: conversational fluff, markdown wraps, no JSON for parsing.")