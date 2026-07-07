import numpy as np
from collections import Counter

def predict_next_token(context, temperature=1.0):
    """
    Simulate how an LLM predicts the next token, based on a fixed set
    of candidate words and their base probabilities.

    Lower temperature = more predictable/conservative (safer for medical advice).
    Higher temperature = more random/creative (fine for casual conversation,
    risky for anything requiring consistency or safety).
    """
    probs = {
        "and": 0.3, "with": 0.25, "recommend": 0.2,
        "suggesting": 0.15, "indicating": 0.1
    }
    tokens = list(probs.keys())
    weights = np.array(list(probs.values()))

    # Temperature scaling: raising each probability to the power of (1/temperature)
    # reshapes the distribution. Low temperature exaggerates the gap between
    # high and low probability words (more predictable). High temperature
    # flattens the gap (more random/varied).
    scaled = weights ** (1.0 / temperature)
    scaled = scaled / scaled.sum()  # re-normalize so probabilities sum to 1

    # np.random.choice picks one token, weighted by the scaled probabilities —
    # this is the actual "prediction" step, mimicking how an LLM samples
    # its next word instead of always picking the single top answer.
    return np.random.choice(tokens, p=scaled)


# --- Run the experiment across multiple temperature settings ---

temperatures = [0.1, 0.5, 1.0, 2.0]
num_trials = 200  # Run 200 trials per temperature 
#to see the pattern emerge (instead of 10)

print("--- Temperature Experiment Results ---")
for temp in temperatures:
    # Run predict_next_token() num_trials times in a row at this temperature.
    # A single prediction wouldn't show us anything meaningful, since it's
    # random either way — we need many repeated trials to see the PATTERN.
    results = [predict_next_token("patient has fever", temp) for _ in range(num_trials)]

    # Counter tallies how many times each word appeared across all trials.
    counts = Counter(results)

    # most_common(1) gives us the single most-picked word and its count —
    # this shows how "dominant" one answer is at this temperature.
    top_token, top_count = counts.most_common(1)[0]

    # len(counts) tells us how many DIFFERENT words showed up at all —
    # at low temperature this should be small (1-2), at high temperature
    # it should be larger (closer to all 5 words appearing at least once).
    print(f"Temp {temp:.1f}: top token = '{top_token}' ({top_count}/{num_trials}); "
          f"unique tokens seen = {len(counts)}")

print("\nRecommendation for AfyaPlus:")
print("  Symptom triage:        temp=0.1-0.3 (consistent, safe responses)")
print("  Greetings:             temp=0.7-1.0 (natural variety)")
print("  Appointment reminders: temp=0.2-0.4 (accurate but slightly varied)")

        # For something like AfyaPlus giving medical guidance, 
        # you'd deliberately want low temperature — you want the same symptom description 
        # to reliably produce similar, safe, consistent guidance every time, 
        # not a different creative answer each time someone asks.