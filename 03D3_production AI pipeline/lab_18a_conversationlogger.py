# =============================================================================
# AFYAPLUS - Further Challenge F: Conversation Logger
# =============================================================================
# =============================================================================
# CONCEPT: Production systems need audit trails. A conversation logger captures
# every interaction with timestamps, token counts, and full message history.
# This enables debugging, compliance reporting, and usage analytics.
# =============================================================================
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()


class ConversationLogger:
    """Logs multi-turn conversations with metadata for audit and analysis."""
    
    def __init__(self, patient_id):
        self.patient_id = patient_id
        self.start_time = datetime.utcnow().isoformat()
        self.messages = []
        self.total_tokens = 0
        self.turns = 0
    
    def add_exchange(self, user_text, assistant_text, tokens_used):
        """Record a user-assistant exchange with timestamp and token count."""
        self.turns += 1
        exchange = {
            "turn": self.turns,
            "timestamp": datetime.utcnow().isoformat(),
            "user_message": user_text,
            "assistant_message": assistant_text,
            "tokens_used": tokens_used
        }
        self.messages.append(exchange)
        self.total_tokens += tokens_used
    
    def save_log(self, path):
        """Save the complete log to a JSON file."""
        end_time = datetime.utcnow().isoformat()
        log_entry = {
            "session_metadata": {
                "patient_id": self.patient_id,
                "start_time": self.start_time,
                "end_time": end_time,
                "total_turns": self.turns,
                "total_tokens": self.total_tokens,
                "average_tokens_per_turn": (
                    self.total_tokens / self.turns if self.turns > 0 else 0
                )
            },
            "messages": self.messages
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(log_entry, f, indent=2, ensure_ascii=False)
        print(f"Log saved to: {path}")


# =============================================================================
# DEMO
# =============================================================================
print("=== Conversation Logger ===\n")

logger = ConversationLogger(patient_id="PAT-2024-0042")

# Turn 1
print("Turn 1...")
r1 = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are AfyaPlus Health Assistant. Be helpful and safe."},
        {"role": "user", "content": "I have had a headache for 3 days"}
    ],
    temperature=0.3,
    max_tokens=100
)
logger.add_exchange("I have had a headache for 3 days", r1.choices[0].message.content, r1.usage.total_tokens)
print(f"   Tokens: {r1.usage.total_tokens}")

# Turn 2
print("Turn 2...")
r2 = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are AfyaPlus Health Assistant. Be helpful and safe."},
        {"role": "user", "content": "Should I take painkillers for it?"}
    ],
    temperature=0.3,
    max_tokens=100
)
logger.add_exchange("Should I take painkillers for it?", r2.choices[0].message.content, r2.usage.total_tokens)
print(f"   Tokens: {r2.usage.total_tokens}")

# Turn 3
print("Turn 3...")
r3 = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are AfyaPlus Health Assistant. Be helpful and safe."},
        {"role": "user", "content": "Now I also feel dizzy when I stand up"}
    ],
    temperature=0.3,
    max_tokens=100
)
logger.add_exchange("Now I also feel dizzy when I stand up", r3.choices[0].message.content, r3.usage.total_tokens)
print(f"   Tokens: {r3.usage.total_tokens}")

# Save
logger.save_log("conversation_log.json")

print(f"\nDone! Patient: {logger.patient_id}, Turns: {logger.turns}, Total tokens: {logger.total_tokens}")

# =============================================================================
# KEY TAKEAWAYS - Conversation Logger
# =============================================================================
# 
# 1. LOG STRUCTURE:
#    - Session metadata: patient_id, times, turns, token totals
#    - Per-turn details: timestamps, messages, individual token counts
#    - JSON format: Human-readable, machine-parseable, importable to databases
#
# 2. PRODUCTION BENEFITS:
#    - Audit trail: Regulators can review every AI-patient interaction
#    - Debugging: Trace exactly what happened in problematic conversations
#    - Analytics: Track token usage, conversation length, common topics
#    - Compliance: Meet healthcare record-keeping requirements
#
# 3. TOKEN TRACKING:
#    - Use response.usage.total_tokens for accurate counts
#    - Track both per-turn and cumulative totals
#    - Enables cost monitoring and usage optimization
# =============================================================================