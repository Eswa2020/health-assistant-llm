# challenge32_hospital_id_mask.py
import re

def mask_pii(text: str) -> str:
    """Mask phone numbers, AfyaPlus IDs, and a NEW hospital ID format."""
    text = re.sub(r"\+?254\d{9}", "[PHONE]", text)      # from Lab 26
    text = re.sub(r"AP-\d{6}", "[PATIENT_ID]", text)     # from Lab 26
    # NEW RULE: HOSP- followed by exactly 8 digits
    text = re.sub(r"HOSP-\d{8}", "[HOSPITAL_ID]", text)
    return text

raw = "Call +254712345678 about AP-004217 / HOSP-20451187 (chest pain)."
print(mask_pii(raw))