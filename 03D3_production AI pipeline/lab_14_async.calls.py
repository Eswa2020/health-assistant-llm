# =============================================================================
# AFYAPLUS - Labs 14 & 15: Synchronous vs Asynchronous API Calls
# =============================================================================
# CONCEPT: Synchronous calls block (wait for each to finish before starting next).
# Asynchronous calls run concurrently (start all at once, collect results as they arrive).
# At production scale with hundreds of patients/minute, async is the difference between
# a responsive system and an unresponsive one.
# =============================================================================

# =============================================================================
# LAB 14: SYNCHRONOUS BASELINE (sync_calls.py)
# =============================================================================
import os
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()  # # Synchronous client - each call blocks until complete

patient_messages = [
    "I have a persistent cough for two weeks",
    "My child has a rash on their arms",
    "I feel dizzy when I stand up quickly"
]

SYSTEM_PROMPT = "You are the AfyaPlus Health Assistant. Provide brief, safe guidance in 2-3 sentences."

print("=== LAB 14: Synchronous Baseline ===")
start_time = time.time()

# # SYNCHRONOUS LOOP: Each iteration waits for the API response before continuing.
# # Patient 2 cannot start until Patient 1 finishes. Patient 3 waits for Patient 2.
# # Total time ≈ sum of all individual call times (3 calls × ~1.5s = ~4.5s)
for i, message in enumerate(patient_messages, 1):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ],
        temperature=0.3,
        max_tokens=100
    )
    print(f"Patient {i}: {message}")
    print(f"Response: {response.choices[0].message.content}")
    print()

total_time = time.time() - start_time
print(f"Total time (synchronous): {total_time:.2f} seconds")
print(f"Average per patient: {total_time/3:.2f} seconds")
# # BASELINE RESULT: ~4-5 seconds total. This is the number async must beat.
print()


# =============================================================================
# LAB 15: ASYNCHRONOUS PRODUCTION PATTERN (async_calls.py)
# =============================================================================
import asyncio
from openai import AsyncOpenAI

# # ASYNC CLIENT: AsyncOpenAI instead of OpenAI - enables non-blocking calls
async_client = AsyncOpenAI()

# # Same messages and system prompt as sync version for fair comparison
patient_messages = [
    "I have a persistent cough for two weeks",
    "My child has a rash on their arms",
    "I feel dizzy when I stand up quickly"
]

SYSTEM_PROMPT = "You are the AfyaPlus Health Assistant. Provide brief, safe guidance in 2-3 sentences."

# # ASYNC FUNCTION: 'async def' + 'await' enables non-blocking execution
# # Each call runs independently; the event loop switches between them while waiting
async def process_patient(message, patient_id):
    """
    Process a single patient message asynchronously.
    
    # WHY async/await?: The 'await' keyword tells Python "this will take time,
    # go work on other tasks while waiting." Without it, we'd block like sync code.
    # The event loop handles switching between pending tasks automatically.
    """
    response = await async_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ],
        temperature=0.3,
        max_tokens=100
    )
    return f"Patient {patient_id}: {response.choices[0].message.content}"

async def main():
    """
    Orchestrates concurrent patient processing.
    
    # asyncio.gather(): The key to parallelism. Takes multiple coroutines,
    # starts them ALL simultaneously, and returns when ALL complete.
    # Total time ≈ slowest single call, not sum of all calls.
    # For 3 calls at ~1.5s each: sync ≈ 4.5s, async ≈ 1.5-1.8s.
    """
    print("=== LAB 15: Asynchronous Production Pattern ===")
    start_time = time.time()
    
    # # Create a task for each patient message
    # # Tasks are lightweight - they don't start executing until gathered
    tasks = [process_patient(msg, i) for i, msg in enumerate(patient_messages, 1)]
    
    # # asyncio.gather(*tasks): Runs all tasks concurrently
    # # The event loop interleaves execution: while one task waits for API,
    # # another task can make progress. This is cooperative multitasking.
    results = await asyncio.gather(*tasks)
    
    # # Results arrive in the same order as tasks were created
    for result in results:
        print(result)
        print()
    
    total_time = time.time() - start_time
    print(f"Total time (asynchronous): {total_time:.2f} seconds")
    print("Speedup: All 3 processed in parallel!")
    print(f"Sync would take ~{total_time*3:.1f}s for the same work")
    print()

# # Run the async main function - this is the entry point for async code
asyncio.run(main())


# =============================================================================
# CHALLENGE: Five Patients in Parallel (challenge11_five_parallel.py)
# =============================================================================
async def challenge_five_parallel():
    """
    Extended version with 5 patients to demonstrate async scaling.
    
    # KEY INSIGHT: Adding more patients doesn't linearly increase time.
    # The total time stays close to the slowest single call because
    # all 5 run concurrently. Sync would take 5× longer.
    # This is why production systems MUST use async for multi-user scenarios.
    """
    print("=== CHALLENGE: Five Patients in Parallel ===")
    
    # # Five diverse patient messages covering different medical scenarios
    patient_messages = [
        "I have a persistent cough for two weeks",
        "My child has a rash on their arms",
        "I feel dizzy when I stand up quickly",
        # # ADDED: Realistic patient message - abdominal pain is common
        "I have had stomach pain after eating for the past three days",
        # # ADDED: Realistic patient message - sleep issues are frequent complaints
        "I cannot sleep more than 3 hours a night and feel exhausted all day"
    ]
    
    start_time = time.time()
    
    # # Same pattern as Lab 15 - asyncio.gather scales automatically
    # # No code changes needed to go from 3 to 5 (or 50) patients
    tasks = [process_patient(msg, i) for i, msg in enumerate(patient_messages, 1)]
    results = await asyncio.gather(*tasks)
    
    for result in results:
        print(result)
        print()
    
    total_time = time.time() - start_time
    print(f"Total time (5 patients async): {total_time:.2f} seconds")
    print(f"Average per patient: {total_time/5:.2f} seconds")
    
    # # COMPARISON: Show what sync would have taken
    estimated_sync_time = total_time * 5  # Sync would be ~5× slower
    print(f"Estimated sync time for 5 patients: ~{estimated_sync_time:.1f} seconds")
    print(f"Speedup factor: ~5x faster with async")
    print()

# Run the challenge
asyncio.run(challenge_five_parallel())


# =============================================================================
# KEY TAKEAWAYS & REFERENCE NOTES
# =============================================================================
# 
# 1. SYNCHRONOUS vs ASYNCHRONOUS:
#    - Sync: Blocking, sequential, simple code, limited throughput
#    - Async: Non-blocking, concurrent, async/await syntax, high throughput
#    - Key difference: Total time ≈ sum of calls (sync) vs ≈ slowest call (async)
#
# 2. THREE KEY ASYNC CHANGES:
#    - Client: AsyncOpenAI() instead of OpenAI()
#    - Functions: 'async def' + 'await' for API calls
#    - Orchestration: asyncio.gather(*tasks) for concurrent execution
#
# 3. WHY ASYNC MATTERS AT SCALE:
#    - AfyaPlus: 100s of patients/minute
#    - Sync: 100 patients × 1.5s = 150 seconds (unacceptable)
#    - Async: 100 patients concurrently ≈ 2-3 seconds (acceptable)
#    - Difference between responsive and unusable system
#
# 4. asyncio.gather() PATTERN:
#    - Takes list of coroutines, runs all simultaneously
#    - Returns results in same order as input tasks
#    - Scales automatically: same code for 3 or 300 patients
#    - Error handling: one failure can cancel all (use return_exceptions=True for resilience)
#
# 5. PRODUCTION CONSIDERATIONS:
#    - FastAPI uses async natively - this pattern IS production code
#    - Connection pooling: AsyncOpenAI manages connections efficiently
#    - Rate limiting: Still bound by API rate limits even with async
#    - Timeout handling: Add asyncio.timeout() for production robustness
#    - Don't mix sync and async: pick one pattern per codebase
# =============================================================================