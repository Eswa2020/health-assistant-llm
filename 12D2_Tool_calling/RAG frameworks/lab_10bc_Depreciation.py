# challenge9_depreciation_methods.py
#----------------------------------------------------------------------------------------#
#   As the AfyaPlus Finance Analyst, compare depreciation methods across asset types.
#   - Straight-line: steady-wear assets (e.g. clinic computers)
#   - Declining-balance (curve): fast-depreciating assets (e.g. ambulance vans)
#   - Instant write-off: low-value/consumable assets expensed fully in year one
#   - Units-of-production: usage-driven wear assets (e.g. diagnostic lab analyzers)
#----------------------------------------------------------------------------------------#
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_core.callbacks import StdOutCallbackHandler
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# --- Tool 1: Straight-line depreciation ---
@tool
def calculate_straight_line_depreciation(initial_cost: float, salvage_value: float, useful_life_years: int) -> str:
    """Calculates annual straight-line depreciation for a clinic asset that wears
    evenly over time — best suited to computers, furniture, or fixed equipment."""
    if useful_life_years <= 0:
        return "Error: useful life must be positive; division by zero is prohibited."
    if initial_cost < 0 or salvage_value < 0:
        return "Error: cost and salvage value must be non-negative."
    if salvage_value > initial_cost:
        return "Error: salvage value cannot exceed initial cost."

    annual = (initial_cost - salvage_value) / useful_life_years
    return f"Straight-line annual depreciation: {annual:.2f}"


# --- Tool 2: Declining-balance depreciation ---
@tool
def calculate_declining_balance_depreciation(initial_cost: float, salvage_value: float, useful_life_years: int) -> str:
    """Calculates a year-by-year double-declining balance (curve) depreciation
    schedule for assets that lose most value early, e.g. ambulance vans or vehicles."""
    if useful_life_years <= 0:
        return "Error: useful life must be positive; division by zero is prohibited."
    if initial_cost < 0 or salvage_value < 0:
        return "Error: cost and salvage value must be non-negative."
    if salvage_value > initial_cost:
        return "Error: salvage value cannot exceed initial cost."

    rate = 2 / useful_life_years
    book_value = initial_cost
    schedule = []

    for year in range(1, useful_life_years + 1):
        depreciation = book_value * rate
        if book_value - depreciation < salvage_value:
            depreciation = book_value - salvage_value
        book_value -= depreciation
        schedule.append(f"Year {year}: {depreciation:.2f} (book value: {book_value:.2f})")

    breakdown = " | ".join(schedule)
    return f"Declining-balance depreciation schedule: {breakdown}"


# --- Tool 3: Instant write-off ---
@tool
def calculate_instant_writeoff_depreciation(initial_cost: float, salvage_value: float) -> str:
    """Calculates instant (full) write-off depreciation for low-value or
    quickly-obsolete items, e.g. basic diagnostic kits or small tools."""
    if initial_cost < 0 or salvage_value < 0:
        return "Error: cost and salvage value must be non-negative."
    if salvage_value > initial_cost:
        return "Error: salvage value cannot exceed initial cost."

    depreciation = initial_cost - salvage_value
    return f"Instant write-off depreciation (Year 1, full amount): {depreciation:.2f}"


# --- Tool 4: Units-of-production depreciation ---
@tool
def calculate_units_of_production_depreciation(
    initial_cost: float,
    salvage_value: float,
    total_estimated_units: float,
    units_this_year: float,
) -> str:
    """Calculates depreciation based on actual usage rather than time — best suited
    to assets like a lab analyzer depreciated per test processed."""
    if total_estimated_units <= 0:
        return "Error: total estimated units must be greater than zero; division by zero is prohibited."
    if initial_cost < 0 or salvage_value < 0:
        return "Error: cost and salvage value must be non-negative."
    if salvage_value > initial_cost:
        return "Error: salvage value cannot exceed initial cost."
    if units_this_year < 0:
        return "Error: units produced this year cannot be negative."
    if units_this_year > total_estimated_units:
        return "Error: units produced this year cannot exceed total estimated lifetime units."

    depreciation_per_unit = (initial_cost - salvage_value) / total_estimated_units
    annual_depreciation = depreciation_per_unit * units_this_year

    return (
        f"Depreciation per unit: {depreciation_per_unit:.2f}. "
        f"Units-of-production depreciation for {units_this_year:.0f} units this year: "
        f"{annual_depreciation:.2f}."
    )


# --- LLM setup ---
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
tools = [
    calculate_straight_line_depreciation,
    calculate_declining_balance_depreciation,
    calculate_instant_writeoff_depreciation,
    calculate_units_of_production_depreciation,
]

# --- Prompt template ---
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are the AfyaPlus Finance Analyst."),
    ("human", "{input}"),
])
system_prompt_text = prompt_template.messages[0].prompt.template

# --- Create the agent ---
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt_text,
)

# --- Test 1: Straight-Line ---
print("=== Test 1: Straight-Line ===")
result_1 = agent.invoke(
    {"messages": [HumanMessage(content="Computer: cost 120,000, salvage 20,000, life 4 years. Annual depreciation?")]},
    config={"callbacks": [StdOutCallbackHandler()]}
)
print("\n--- Final Answer ---")
print(result_1["messages"][-1].content)

# --- Test 2: Declining Balance ---
print("\n\n=== Test 2: Declining Balance ===")
result_2 = agent.invoke(
    {"messages": [HumanMessage(content="Ambulance van: cost 3,500,000, salvage 500,000, life 5 years. Depreciation schedule?")]},
    config={"callbacks": [StdOutCallbackHandler()]}
)
print("\n--- Final Answer ---")
print(result_2["messages"][-1].content)

# --- Test 3: Instant Write-Off ---
print("\n\n=== Test 3: Instant Write-Off ===")
result_3 = agent.invoke(
    {"messages": [HumanMessage(content="Diagnostic kit: cost 8,000, no salvage value. What's the depreciation?")]},
    config={"callbacks": [StdOutCallbackHandler()]}
)
print("\n--- Final Answer ---")
print(result_3["messages"][-1].content)

# --- Test 4: Units-of-Production ---
print("\n\n=== Test 4: Units-of-Production ===")
result_4 = agent.invoke(
    {"messages": [HumanMessage(content="Lab analyzer: cost 900,000, salvage 100,000, rated for 400,000 tests, processed 62,000 this year. Depreciation?")]},
    config={"callbacks": [StdOutCallbackHandler()]}
)
print("\n--- Final Answer ---")
print(result_4["messages"][-1].content)

# --- Test 5: Multi-Asset — All Four Methods ---
print("\n\n=== Test 5: Multi-Asset — All Four Methods ===")
result_5 = agent.invoke(
    {"messages": [HumanMessage(content=(
        "Cost out four assets: ambulance van (3,500,000 / salvage 500,000 / 5yrs, declining-balance), "
        "monitoring equipment (450,000 / salvage 50,000 / 5yrs, straight-line), "
        "diagnostic kits (8,000 / no salvage, instant write-off), "
        "and lab analyzer (900,000 / salvage 100,000 / 400,000 rated tests / 62,000 used this year, units-of-production)."
    ))]},
    config={"callbacks": [StdOutCallbackHandler()]}
)
print("\n--- Final Answer ---")
print(result_5["messages"][-1].content)