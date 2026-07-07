import numpy as np

# Simulated 3D word embeddings.
# Each dimension represents: [Clinical-Symptom, Administrative, Time/Urgency]
embeddings = {
    "fever":     np.array([0.9, 0.0, 0.3]),
    "pain":      np.array([0.8, 0.1, 0.4]),
    "discharge": np.array([0.5, 0.5, 0.1]), # Ambiguous word!
    "billing":   np.array([0.0, 0.9, 0.1]),
    "admit":     np.array([0.2, 0.8, 0.2])
}

def cosine_similarity(word1, word2):
    """Calculate how close two words are in embedding space."""
    vec1 = embeddings[word1]
    vec2 = embeddings[word2]
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# If 'discharge' appears alongside 'pain', it is likely a clinical symptom.
# If it appears alongside 'billing', it is administrative.
print("--- Context-Disambiguation via Cosine Similarity ---")
print(f"Context Match (Discharge + Pain):    {cosine_similarity('discharge', 'pain'):.4f}")
print(f"Context Match (Discharge + Billing): {cosine_similarity('discharge', 'billing'):.4f}")
print(f"Context Match (Fever + Pain): {cosine_similarity('fever', 'pain'):.4f}")
print(f"Context Match (Fever + Admit): {cosine_similarity('fever', 'admit'):.4f}")

import numpy as np

embeddings = {
    "fever":     np.array([0.9, 0.0, 0.3]),
    "pain":      np.array([0.8, 0.1, 0.4]),
    "discharge": np.array([0.5, 0.5, 0.1]),
    "billing":   np.array([0.0, 0.9, 0.1]),
    "admit":     np.array([0.2, 0.8, 0.2]),
    "cough":    np.array([0.85,0.05,0.35])  # Added 'cough' vector close to 'fever' from 'billing'
   
    # TODO 1: Add a 'cough' vector that sits close to 'fever' and far from 'billing'.
}

def cosine_similarity(word1, word2):
    vec1, vec2 = embeddings[word1], embeddings[word2]
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# TODO 2: Print cosine_similarity('cough', 'fever') and cosine_similarity('cough', 'billing')
print(f"Context Match (Cough + Fever): {cosine_similarity('cough', 'fever'):.4f}")
print(f"Context Match (Cough + Billing): {cosine_similarity('cough', 'billing'):.4f}")


# TODO 3: Confirm the fever score is meaningfully higher than the billing score.
fever_score = cosine_similarity('cough', 'fever')
billing_score = cosine_similarity('cough', 'billing')
print(f"\nIs 'cough' more clinical than administrative? {fever_score > billing_score}")
print(f"Difference: {fever_score - billing_score:.4f}")
# Explanation: this is the actual "proof" step. We're not just eyeballing
# the numbers — we're programmatically checking that the fever similarity
# score is higher than the billing similarity score. If True, it confirms
# our embedding design worked: 'cough' correctly clusters with clinical
# symptom words rather than administrative ones, purely because of how
# we chose its vector values above.