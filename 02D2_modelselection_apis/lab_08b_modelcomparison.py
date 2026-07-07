import os
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
cloud_client = OpenAI()
local_client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

SYSTEM_PROMPT = "You are a health assistant. Provide brief, safe guidance."
patient_message = "I have chest pain when I breathe deeply"

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": patient_message}
]

# TODO 1: time the cloud call and store the response
start_cloud = time.time()
cloud_response = cloud_client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    temperature=0.3
)
end_cloud = time.time()
cloud_time = end_cloud - start_cloud

# TODO 2: time the local call and store the response
start_local = time.time()
local_response = local_client.chat.completions.create(
    model="llama3.2",
    messages=messages,
    temperature=0.3
)
end_local = time.time()
local_time = end_local - start_local

# TODO 3: print a 3-row comparison: time, response length, first 200 chars

cloud_text = cloud_response.choices[0].message.content
local_text = local_response.choices[0].message.content

print("--- Cloud vs Local Comparison ---")
print(f"\nCloud (gpt-4o-mini):")
print(f"  Time taken: {cloud_time:.2f} seconds")
print(f"  Response length: {len(cloud_text)} characters")
print(f"  First 200 chars: {cloud_text[:200]}")

print(f"\nLocal (llama3.2):")
print(f"  Time taken: {local_time:.2f} seconds")
print(f"  Response length: {len(local_text)} characters")
print(f"  First 200 chars: {local_text[:200]}")