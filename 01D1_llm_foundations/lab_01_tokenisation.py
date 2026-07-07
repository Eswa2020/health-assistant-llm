import numpy as np

def simple_numpy_tokenizer(text):
    # 1. Basic cleaning and splitting
    # We convert to lowercase and remove simple punctuation
    clean_text = text.lower().replace(".", "").replace("?", "")
    tokens = clean_text.split()

    # 2. Convert to NumPy array
    token_array = np.array(tokens)

    # 3. Create a vocabulary (unique tokens)
    # This represents the internal 'dictionary' our system recognises
    vocab, inverse_indices = np.unique(token_array, return_inverse=True)

    return token_array, vocab, inverse_indices

# Real patient case from the AfyaPlus portal
patient_query = "My chest hurts. Is it a heart attack?"
tokens, vocabulary, token_ids = simple_numpy_tokenizer(patient_query)

print("--- Tokenisation Results ---")
print(f"Original Text: {patient_query}")
print(f"Tokens: {tokens}")
print(f"Vocabulary: {vocabulary}")
print(f"Token IDs (Numerical Representation): {token_ids}")


import numpy as np

def emergency_tokeniser(text):
    """Split text into tokens while preserving '!' as separate tokens."""
    text = text.lower()

    # TODO 1: Pad '!' with spaces so split() treats them as separate tokens.
    text = text.replace("!", " ! ")

    # TODO 2: Remove any other punctuation that should not be a token.
    text = text.replace(".", "")
    text = text.replace("?", "")
    text = text.replace(",", "")

    # TODO 3: Split on whitespace and return a NumPy array.
    tokens = np.array(text.split())
    return tokens

# Test cases
samples = ["Help!!!", "I cannot breathe!", "My chest hurts."]
for s in samples:
    print(s, "->", emergency_tokeniser(s))

# Expected for "Help!!!": ['help', '!', '!', '!']