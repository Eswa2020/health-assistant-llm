# wk2_challenge2_diagnostic_triage_precaution.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0.2)

# --- Prompt Templates ---
prompt_explanation = ChatPromptTemplate.from_template(
    "You are an AfyaPlus triage assistant. Draft a brief, structured preliminary "
    "triage assessment for this condition: {condition}. Describe likely symptoms "
    "and general urgency. Do not prescribe medication."
)

prompt_precaution = ChatPromptTemplate.from_template(
    "Review this triage assessment and append an explicit medication-safety "
    "caution warning patients not to self-medicate without consulting a "
    "healthcare professional:\n\n{explanation}"
)

prompt_translation = ChatPromptTemplate.from_template(
    "Combine this triage note and this safety precaution into one short, clear "
    "Swahili SMS message for a patient:\n\nTriage note: {explanation}\n\n"
    "Precaution: {precaution}"
)

# --- LCEL Engine Piping ---
chain_explanation = prompt_explanation | llm | StrOutputParser()
chain_precaution = prompt_precaution | llm | StrOutputParser()
chain_translation = prompt_translation | llm | StrOutputParser()

# --- Execution Runtime ---
target_condition = "High fever accompanied by severe chills (Suspected Malaria)"
print(f"Target Condition: {target_condition}\n")

# Step 1: Invoke chain 1 to get the explanation
explanation_output = chain_explanation.invoke({"condition": target_condition})

# Step 2: Invoke chain 2, feeding in chain 1's output
precaution_output = chain_precaution.invoke({"explanation": explanation_output})

# Step 3: Invoke chain 3, feeding in BOTH prior outputs at once
final_swahili_sms = chain_translation.invoke({
    "explanation": explanation_output,
    "precaution": precaution_output
})

print(f"Generated Explanation: {explanation_output}\n")
print(f"Generated Precaution: {precaution_output}\n")
print(f"Final Swahili SMS Wire: {final_swahili_sms}")