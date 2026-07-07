import numpy as np

def simple_numpy_tokenizer(text):
    clean_text = text.lower().replace(".", "").replace("?", "").replace(",", "")
    tokens = clean_text.split()
    return np.array(tokens)

original_query = (
    "Hujambo, it is Juma. I am feeling very hot, my head hurts since yesterday, "
    "and I am coughing. I cannot go to the clinic because of the rain. What should I do?"
)

# TODO 1: Tokenise the original_query and count the tokens.
original_tokens = simple_numpy_tokenizer(original_query)
original_count = len(original_tokens)
print(f"Original tokens ({original_count}): {original_tokens}")

# TODO 2: Manually rewrite the query as a 10-word summary of the medical facts only.
# Strips greeting, filler, and the rain/logistics detail — keeps only symptoms.
summary_query = "Fever, headache since yesterday, persistent dry cough, no other symptoms."

# TODO 3: Tokenise the summary and count the tokens.
summary_tokens = simple_numpy_tokenizer(summary_query)
summary_count = len(summary_tokens)
print(f"Summary tokens ({summary_count}): {summary_tokens}")

# TODO 4: Calculate the percentage of tokens saved.
tokens_saved = original_count - summary_count
pct_saved = (tokens_saved / original_count) * 100
print(f"Tokens saved per query: {tokens_saved} ({pct_saved:.2f}%)")

# TODO 5: If 1,000 users send this query daily, how many tokens are saved per month (30 days).
users_per_day = 1000
days_per_month = 30
monthly_tokens_saved = tokens_saved * users_per_day * days_per_month
print(f"Monthly tokens saved: {monthly_tokens_saved:,}")