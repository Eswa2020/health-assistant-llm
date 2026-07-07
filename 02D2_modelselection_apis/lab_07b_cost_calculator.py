def estimate_monthly_cost(avg_input_tokens, avg_output_tokens,
                          daily_messages, days_per_month=30):
    """
    Calculate estimated monthly API costs for AfyaPlus.
    GPT-4o-mini pricing:
    - Input:  $0.15 per 1,000,000 tokens
    - Output: $0.60 per 1,000,000 tokens
    """
    # Step 1 & 2: total monthly tokens
    # First get tokens per day, then scale up to a full month
    monthly_input_tokens = avg_input_tokens * daily_messages * days_per_month
    monthly_output_tokens = avg_output_tokens * daily_messages * days_per_month

    # Step 3: convert token counts into dollars
    # Divide by 1,000,000 first (since pricing is "per million tokens"),
    #THEN multiply by the price per million like below then multiply 
    #by price per million token
    input_cost = (monthly_input_tokens / 1_000_000) * 0.15
    output_cost = (monthly_output_tokens / 1_000_000) * 0.60

    # Step 4: total and return as a dictionary
    total_monthly = input_cost + output_cost

    return {
        "monthly_input_tokens": monthly_input_tokens,
        "monthly_output_tokens": monthly_output_tokens,
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_monthly": total_monthly
    }


# Test: 5,000 messages/day, avg 100 input + 150 output tokens
result = estimate_monthly_cost(
    avg_input_tokens=200,
    avg_output_tokens=300,
    daily_messages=50000
)
print(f"Monthly input tokens: {result['monthly_input_tokens']:,}")
print(f"Monthly output tokens: {result['monthly_output_tokens']:,}")
print(f"Input cost: ${result['input_cost']:.2f}")
print(f"Output cost: ${result['output_cost']:.2f}")
print(f"Monthly cost estimate: ${result['total_monthly']:.2f}")