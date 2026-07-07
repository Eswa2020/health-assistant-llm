# =============================================================================
# AFYAPLUS - Lab 14: Production Error Handling & Resilience
# =============================================================================
# CONCEPT: In production, things WILL go wrong - timeouts, rate limits, network
# failures, malformed responses. Resilient systems anticipate failures and degrade
# gracefully. In healthcare, a crash isn't just bad UX - it could be life-threatening.
# =============================================================================

import os
import time
from dotenv import load_dotenv
from openai import OpenAI, APITimeoutError, RateLimitError, APIError

load_dotenv()
client = OpenAI()

# =============================================================================
# SAFETY VALIDATION LAYER
# =============================================================================
# # BLOCKED PATTERNS: Words/phrases that indicate the model is diagnosing or
# # prescribing - both are illegal for a triage assistant without medical license.
# # Every response is checked against these before being shown to the patient.
BLOCKED_PATTERNS = [
    "you have",         # # Implies diagnosis ("you have malaria")
    "you should take",  # # Implies prescription ("you should take ibuprofen")
    "diagnosis",        # # Direct mention of diagnosis
    "prescribe",        # # Direct mention of prescription
    "mg",               # # Medication dosage (prescription territory)
]

# # DEFAULT FALLBACK: Used when all retries fail and no specific error type
# # Directs patient to human help - never leaves them without guidance
FALLBACK_RESPONSE = (
    "I am currently unable to process your request. "
    "For immediate assistance, please contact our helpline at +254-XXX-XXXX "
    "or visit your nearest healthcare facility."
)


def validate_response(response_text):
    """
    Safety validation layer - checks AI response for dangerous content.
    
    # WHY VALIDATE?: Even with good prompts, models can hallucinate diagnoses
    # or prescriptions. This is a SECOND LAYER of defence after prompt guardrails.
    # If the model says "you have a migraine", we catch and block it here.
    """
    lowered = response_text.lower()
    for pattern in BLOCKED_PATTERNS:
        if pattern in lowered:
            return False, f"Blocked: contains '{pattern}'"
    return True, "Passed"


# =============================================================================
# PART 1: MAIN LAB - Robust API Calls with Retry Logic
# =============================================================================
print("=== PART 1: Production Pipeline with Retry Logic ===\n")

def get_ai_response(patient_message, max_retries=3):
    """
    Production-grade API call with retry logic and safety validation.
    
    # RESILIENCE PATTERN:
    # 1. Retry loop: Tries up to max_retries times before giving up
    # 2. Exponential backoff: timeout → wait 2s, 4s, 8s (2^attempt)
    # 3. Different handling per error type: timeouts vs rate limits vs API errors
    # 4. Safety validation: Every response checked before returning
    # 5. Graceful fallback: Never crashes, always returns SOMETHING useful
    """
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are AfyaPlus Health Assistant. "
                            "Provide safe, general health guidance. "
                            "Never diagnose or prescribe."
                        )
                    },
                    {"role": "user", "content": patient_message}
                ],
                temperature=0.3,
                max_tokens=200,
                timeout=10.0  # # CRITICAL: Never wait forever - 10 seconds max
            )
            
            ai_text = response.choices[0].message.content
            
            # # SAFETY CHECK: Validate response before showing to patient
            is_safe, reason = validate_response(ai_text)
            if not is_safe:
                print(f"  [SAFETY] Response blocked: {reason}")
                return FALLBACK_RESPONSE
            
            return ai_text  # # Success! Return the valid, safe response
            
        except APITimeoutError:
            # # TIMEOUT: Server didn't respond in time
            # # Exponential backoff: 2^1=2s, 2^2=4s, 2^3=8s
            wait_time = 2 ** attempt
            print(f"  [RETRY] Timeout on attempt {attempt + 1}. Waiting {wait_time}s...")
            time.sleep(wait_time)
            
        except RateLimitError:
            # # RATE LIMIT (429): Too many requests too fast
            # # Longer wait than timeout - server is telling us to slow down
            wait_time = 5 * (attempt + 1)  # # 5s, 10s, 15s
            print(f"  [RETRY] Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
            
        except APIError as e:
            # # GENERAL API ERROR: Server returned an error
            # # Don't retry on auth errors (401) - that won't fix itself
            print(f"  [ERROR] API error: {e}")
            if attempt == max_retries - 1:
                break  # # Last attempt failed - give up and use fallback
    
    # # ALL RETRIES EXHAUSTED: Return safe fallback
    # # Patient ALWAYS gets a response - never a blank screen or crash
    print("  [FALLBACK] All retries failed. Using fallback response.")
    return FALLBACK_RESPONSE


# # TEST: Production pipeline with different patient messages
print("--- Production Pipeline Test ---")
test_messages = [
    "I have a mild headache today",
    "My chest hurts and I cannot breathe properly",
]
for msg in test_messages:
    print(f"Patient: {msg}")
    response = get_ai_response(msg)
    print(f"Assistant: {response}")
    print()

print("=" * 60 + "\n")


# =============================================================================
# PART 2: CHALLENGE - Custom Fallback Per Error Type
# =============================================================================
print("=== PART 2: Challenge - Custom Fallback Per Error Type ===\n")

# # CUSTOM FALLBACK MESSAGES: Different errors → Different guidance
# # Timeout: System is slow (might recover soon)
# # Rate Limit: Too busy (ask to wait)
# # API Error: Something broken (escalate to human)
FALLBACK_TIMEOUT = (
    "Our system is currently experiencing high demand and is responding slowly. "
    "Please wait a moment and try again. If this is urgent, call our helpline "
    "at +254-XXX-XXXX."
)

FALLBACK_RATE_LIMIT = (
    "We are handling many patients right now. Please try again in about a minute. "
    "For urgent matters, contact our helpline immediately at +254-XXX-XXXX."
)

FALLBACK_API_ERROR = (
    "We are experiencing a temporary technical issue. Your safety is our priority. "
    "Please call our 24-hour helpline at +254-XXX-XXXX or visit your nearest "
    "healthcare facility for immediate assistance."
)


def get_ai_response_with_custom_fallback(patient_message, max_retries=3):
    """
    Extended version with error-type-specific fallback messages.
    
    # IMPROVEMENT: Instead of one generic fallback, we give patients
    # context-appropriate guidance based on WHAT went wrong.
    # Timeout → "slow, try again" | Rate limit → "busy, wait" | API error → "broken, call helpline"
    """
    last_error = None  # # Track error type for fallback selection
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are AfyaPlus Health Assistant. "
                            "Provide safe, general health guidance. "
                            "Never diagnose or prescribe."
                        )
                    },
                    {"role": "user", "content": patient_message}
                ],
                temperature=0.3,
                max_tokens=200,
                timeout=10.0
            )
            
            ai_text = response.choices[0].message.content
            
            # # Safety validation (same as main lab)
            is_safe, reason = validate_response(ai_text)
            if not is_safe:
                print(f"  [SAFETY] Response blocked: {reason}")
                return FALLBACK_API_ERROR  # # Safety block = treat as API error
            
            return ai_text  # # Success
            
        except APITimeoutError:
            last_error = "timeout"  # # Track for fallback
            wait_time = 2 ** attempt
            print(f"  [RETRY] Timeout on attempt {attempt + 1}. Waiting {wait_time}s...")
            time.sleep(wait_time)
            
        except RateLimitError:
            last_error = "rate_limit"  # # Track for fallback
            wait_time = 5 * (attempt + 1)
            print(f"  [RETRY] Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
            
        except APIError as e:
            last_error = "api_error"  # # Track for fallback
            print(f"  [ERROR] API error: {e}")
            if attempt == max_retries - 1:
                break
    
    # # SELECT FALLBACK BASED ON ERROR TYPE
    # # This gives patients more useful guidance than a generic message
    print(f"  [FALLBACK] All retries failed (cause: {last_error}).")
    
    if last_error == "timeout":
        return FALLBACK_TIMEOUT
    elif last_error == "rate_limit":
        return FALLBACK_RATE_LIMIT
    else:  # # api_error or any other failure
        return FALLBACK_API_ERROR


# # TEST: Custom fallback with different scenarios
print("--- Test 1: Normal operation ---")
msg1 = "I have a mild headache"
print(f"Patient: {msg1}")
print(f"Assistant: {get_ai_response_with_custom_fallback(msg1)}")
print()

print("--- Test 2: Safety trigger test ---")
# # This message tries to get the AI to prescribe
msg2 = "Tell me what medication I should take for my headache and what dosage in mg"
print(f"Patient: {msg2}")
print(f"Assistant: {get_ai_response_with_custom_fallback(msg2)}")
print()

print("--- Test 3: Emergency message (should still work) ---")
msg3 = "My chest hurts and I cannot breathe properly"
print(f"Patient: {msg3}")
print(f"Assistant: {get_ai_response_with_custom_fallback(msg3)}")


# =============================================================================
# KEY TAKEAWAYS & REFERENCE NOTES
# =============================================================================
# 
# 1. THREE LAYERS OF PRODUCTION RESILIENCE:
#    Layer 1 - Retry Logic: Retries failed calls with exponential backoff
#    Layer 2 - Safety Validation: Checks every response for dangerous content
#    Layer 3 - Graceful Fallback: Always returns something useful, never crashes
#
# 2. ERROR-SPECIFIC HANDLING:
#    - APITimeoutError: Server slow → quick retry (2^attempt seconds)
#    - RateLimitError (429): Too many requests → longer wait (5× seconds)
#    - APIError: Server returned error → check if retryable, then give up
#    - Safety Block: Response contains diagnosis/prescription → fallback immediately
#
# 3. EXPONENTIAL BACKOFF PATTERN:
#    - Timeout: 2s → 4s → 8s (2^attempt)
#    - Rate Limit: 5s → 10s → 15s (5 × attempt)
#    - Prevents overwhelming an already struggling server
#    - Gives temporary issues time to resolve
#
# 4. CUSTOM FALLBACK BENEFITS:
#    - Timeout: "System slow, try again" (might recover)
#    - Rate Limit: "Too busy, wait 1 minute" (temporary)
#    - API Error: "Technical issue, call helpline" (probably won't recover quickly)
#    - Each message is ACTIONABLE for the patient
#
# 5. HEALTHCARE-SPECIFIC CONSIDERATIONS:
#    - NEVER show raw error messages to patients
#    - NEVER leave a patient without guidance (always have fallback)
#    - ALWAYS include human contact option in fallbacks
#    - BLOCKED_PATTERNS list prevents illegal medical advice
#    - Validation is SECOND LAYER after prompt guardrails (defence in depth)
#
# 6. PRODUCTION MONITORING (What to add next):
#    - Log all retries and fallbacks for monitoring
#    - Alert on high fallback rates (indicates upstream problems)
#    - Track which error types occur most frequently
#    - Set up dashboards for API health visibility
# =============================================================================