# capstone_masking.py
import re
import uuid

def mask_pii(text: str) -> tuple[str, dict]:
    """
    Detects Kenyan phone numbers and email addresses in raw text,
    replaces each with a unique placeholder token, and returns both
    the masked text and a mapping so the original values can be
    restored later (de-masking).
    """
    pii_map = {}

    # --- Kenyan phone number patterns ---
    # Matches: 07XXXXXXXX, 01XXXXXXXX, +2547XXXXXXXX, +2541XXXXXXXX, 2547XXXXXXXX
    phone_pattern = re.compile(r"(?:\+254|254|0)(7|1)\d{8}")

    # --- Email pattern (standard) ---
    email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

    def replace_phone(match):
        token = f"<PHONE_{uuid.uuid4().hex[:8]}>"
        pii_map[token] = match.group(0)
        return token

    def replace_email(match):
        token = f"<EMAIL_{uuid.uuid4().hex[:8]}>"
        pii_map[token] = match.group(0)
        return token

    # Order matters: mask emails first (so an email containing digits
    # doesn't accidentally get partially matched by the phone pattern)
    masked_text = email_pattern.sub(replace_email, text)
    masked_text = phone_pattern.sub(replace_phone, masked_text)

    return masked_text, pii_map


def unmask_pii(text: str, pii_map: dict) -> str:
    """
    Reverses mask_pii: replaces placeholder tokens in the given text
    with their original values, using the mapping produced during masking.
    """
    for token, original_value in pii_map.items():
        text = text.replace(token, original_value)
    return text


# --- Quick standalone test ---
if __name__ == "__main__":
    sample_input = (
        "Hi, this is Juma. My phone number is 0712345678 and my email "
        "is juma.otieno@example.com. I need help with my clinic appointment."
    )

    masked, mapping = mask_pii(sample_input)
    print("Original:  ", sample_input)
    print("Masked:    ", masked)
    print("PII Map:   ", mapping)

    restored = unmask_pii(masked, mapping)
    print("Restored:  ", restored)
    print("Match original:", restored == sample_input)