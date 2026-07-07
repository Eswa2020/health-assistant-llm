# =============================================================================
# AFYAPLUS - Lab 12: Real-Time Streaming Responses
# =============================================================================
# CONCEPT: Streaming sends AI response token-by-token as generated, instead of
# waiting for the complete response. This dramatically improves perceived
# responsiveness - users see text immediately rather than staring at a blank screen.
# Critical for anxious patients who might think the system is broken.
# =============================================================================

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

# =============================================================================
# MAIN LAB: Streaming Responses
# =============================================================================
print("=== LAB 15: Real-Time Streaming ===")

patient_message = "I have been feeling very tired for the past week and have no appetite."

print(f"Patient: {patient_message}")
# # end="" prevents newline, flush=True forces immediate output without buffering
# # Without flush=True, Python might buffer the output and defeat the streaming effect
print("Assistant: ", end="", flush=True)

try:
    # # STREAMING: stream=True tells OpenAI to send response incrementally
    # # Instead of one complete response object, we get a stream of "chunks"
    # # Each chunk contains a small piece of text (usually a few tokens)
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are the AfyaPlus Health Assistant. Provide brief, empathetic guidance."},
            {"role": "user", "content": patient_message}
        ],
        temperature=0.3,
        max_tokens=200,
        stream=True  # # THE KEY PARAMETER: enables token-by-token streaming
    )

    # # STREAM PROCESSING LOOP: Iterate over chunks as they arrive
    # # Each chunk.choices[0].delta.content contains the new token(s)
    # # delta (not message) because we're getting incremental updates
    full_response = ""  # # Accumulate full response for logging/validation
    for chunk in stream:
        # # Check if this chunk contains text (some chunks are metadata only)
        if chunk.choices[0].delta.content is not None:
            token = chunk.choices[0].delta.content
            # # Print immediately with flush=True for real-time display
            # # This creates the "typing" effect users expect from AI
            print(token, end="", flush=True)
            full_response += token  # # Accumulate for post-processing

    print()  # # Final newline after streaming completes
    print("--- Streaming complete ---")
    print(f"Total response length: {len(full_response)} characters")
    
except Exception as e:
    # # Error handling: Streaming can fail mid-response (network issues, etc.)
    # # Always wrap streaming in try/except for production robustness
    print(f"\nError during streaming: {e}")

print()


# =============================================================================
# CHALLENGE: Streaming with Word Count
# =============================================================================
print("=== CHALLENGE: Streaming with Word Count ===")

patient_message2 = "I have had a sore throat and runny nose for three days. Should I see a doctor?"

print(f"Patient: {patient_message2}")
print("Assistant: ", end="", flush=True)

try:
    stream2 = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are the AfyaPlus Health Assistant. Provide brief, empathetic guidance."},
            {"role": "user", "content": patient_message2}
        ],
        temperature=0.3,
        max_tokens=200,
        stream=True
    )

    # # WORD COUNT TRACKING VARIABLES
    last_milestone = 0  # # Tracks the last multiple-of-10 we printed
    full_response = ""  # # Accumulates response for word counting
    
    for chunk in stream2:
        delta = chunk.choices[0].delta.content
        if delta is None:
            continue  # # Skip metadata-only chunks (no text content)
        
        print(delta, end="", flush=True)
        full_response += delta
        
        # # WORD COUNT LOGIC: Count words by splitting on whitespace
        # # len(full_response.split()) counts words in accumulated text
        current_word_count = len(full_response.split())
        
        # # MILESTONE DETECTION: Print count when crossing a multiple of 10
        # # Integer division (// 10) gives the milestone group number
        # # Compare to last_milestone to avoid printing same milestone twice
        # # Example: word 9 → milestone 0, word 10 → milestone 1 → PRINT
        current_milestone = current_word_count // 10  # # Integer division by 10
        
        if current_milestone > last_milestone:
            # # Inline print with brackets to distinguish from response text
            print(f" [{current_word_count} words]", end="", flush=True)
            last_milestone = current_milestone  # # Update to prevent duplicate prints

    print()
    print("--- Streaming complete ---")
    print(f"Final word count: {len(full_response.split())} words")
    print(f"Total response length: {len(full_response)} characters")
    
except Exception as e:
    print(f"\nError during streaming: {e}")


# =============================================================================
# KEY TAKEAWAYS & REFERENCE NOTES
# =============================================================================
# 
# 1. STREAMING FUNDAMENTALS:
#    - stream=True: Enables token-by-token delivery instead of full response
#    - chunk.choices[0].delta.content: The new token(s) in this chunk
#    - delta (not message): Because we're getting incremental updates
#    - flush=True: Forces immediate output without Python buffering
#    - Perceived latency: <100ms vs 2-3 seconds (massive UX improvement)
#
# 2. WHY STREAMING MATTERS:
#    - Anxious patients see immediate response → trust system is working
#    - Early termination possible if response goes off-track
#    - Reduces perceived wait time dramatically (UX psychology)
#    - Enables real-time UI updates (typing indicators, word counts)
#
# 3. STREAMING LOOP PATTERN:
#    - for chunk in stream: Iterate over incoming chunks
#    - Check delta.content is not None: Skip metadata chunks
#    - print(token, end="", flush=True): Display immediately
#    - Accumulate full_response: For logging, validation, post-processing
#    - try/except: Handle mid-stream failures gracefully
#
# 4. CHUNK STRUCTURE:
#    - Some chunks are metadata-only (delta.content is None)
#    - Text chunks contain 1-3 tokens typically
#    - Last chunk may be empty (signals stream end)
#    - Always check for None before accessing content
#
# 5. WORD COUNT TECHNIQUE:
#    - len(full_response.split()): Simple word counting by whitespace
#    - Integer division (// 10): Groups words into milestones
#    - last_milestone tracking: Prevents duplicate milestone prints
#    - Inline display: Shows progress without breaking response flow
#
# 6. PRODUCTION STREAMING PATTERNS:
#    - Web: Server-Sent Events (SSE) or WebSocket for browser streaming
#    - FastAPI: StreamingResponse for async streaming endpoints
#    - Early termination: Break out of loop if content filter triggers
#    - Timeout handling: Set stream timeout for hung connections
#    - Backpressure: Pause consumption if client can't keep up
#
# 7. SYNC vs ASYNC STREAMING:
#    - This lab uses sync client for clarity
#    - AsyncOpenAI supports streaming with 'async for chunk in stream'
#    - Pattern identical: just add async/await keywords
#    - Both achieve same UX improvement (token-by-token display)
# =============================================================================