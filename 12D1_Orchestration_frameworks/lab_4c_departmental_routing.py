# wk2_challenge3_departmental_routing_pipeline.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm_router = ChatOpenAI(model="gpt-5.4-mini", temperature=0.0)
llm_chain = ChatOpenAI(model="gpt-5.4-mini", temperature=0.2)

# --- TASK 1: DEFINE YOUR COMPONENTS ---
router_prompt = ChatPromptTemplate.from_template(
    "Classify the patient message as exactly one word, either CLINICAL or BILLING.\n"
    "Message: {message}\nClassification:"
)

clinical_template = ChatPromptTemplate.from_template(
    "Draft a 1-sentence medical triage acknowledgement for this message: {message}"
)
billing_template = ChatPromptTemplate.from_template(
    "Draft a 1-sentence billing support acknowledgement for this message: {message}"
)

translation_template = ChatPromptTemplate.from_template(
    "Translate this text into clear Swahili for an SMS alert: {text}"
)

# --- TASK 2: BUILD LCEL PIPELINES ---
router_chain = router_prompt | llm_router | StrOutputParser()
translation_chain = translation_template | llm_chain | StrOutputParser()

clinical_chain = clinical_template | llm_chain | StrOutputParser()
billing_chain = billing_template | llm_chain | StrOutputParser()

# --- TASK 3: CONSTRUCT RUNTIME FLOW ---
incoming_patient_sms = "I need to request an itemized receipt for my outpatient prescription payment."

print(f"Incoming Payload: {incoming_patient_sms}\n")

# Step A: Run the router to classify the message
detected_route = router_chain.invoke({"message": incoming_patient_sms}).strip().upper()

print(f"--- Route Evaluated: {detected_route} ---")

# Step B: Execute the matching chain based on the route
if detected_route == "CLINICAL":
    acknowledgement = clinical_chain.invoke({"message": incoming_patient_sms})
elif detected_route == "BILLING":
    acknowledgement = billing_chain.invoke({"message": incoming_patient_sms})
else:
    acknowledgement = "Route unclear \u2014 escalate to human review."

final_swahili_sms = translation_chain.invoke({"text": acknowledgement})

print(f"English Acknowledgement: {acknowledgement}")
print(f"Final Swahili SMS: {final_swahili_sms}")