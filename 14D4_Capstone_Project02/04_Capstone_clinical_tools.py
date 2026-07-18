# 04_capstone_clinical_tools.py
from langchain_core.tools import tool


@tool
def calculate_medication_dosage(
    patient_weight_kg: float,
    dose_per_kg_mg: float,
) -> str:
    """Calculates the total medication dose (in mg) for a patient based on
    their weight and a standard weight-based dosing rate (mg per kg).
    Used for weight-dependent medications like some antibiotics or
    paediatric dosing."""
    try:
        if patient_weight_kg <= 0:
            return "Error: patient weight must be greater than zero."
        if dose_per_kg_mg <= 0:
            return "Error: dose per kg must be greater than zero."

        total_dose_mg = patient_weight_kg * dose_per_kg_mg
        return f"Total dose: {total_dose_mg:.2f} mg for a {patient_weight_kg:.1f} kg patient."
    except Exception as e:
        return f"Error calculating dosage: {e}"


@tool
def calculate_iv_drip_rate(
    volume_ml: float,
    infusion_time_hours: float,
    drop_factor_gtts_per_ml: float = 20.0,
) -> str:
    """Calculates the IV infusion drip rate in drops per minute (gtts/min),
    given the total volume to infuse (mL), the infusion time (hours), and
    the drop factor of the IV set (drops per mL — commonly 15 or 20 for
    standard sets, 60 for micro-drip sets)."""
    try:
        if volume_ml <= 0:
            return "Error: volume must be greater than zero."
        if infusion_time_hours <= 0:
            return "Error: infusion time must be greater than zero."
        if drop_factor_gtts_per_ml <= 0:
            return "Error: drop factor must be greater than zero."

        infusion_time_minutes = infusion_time_hours * 60
        drip_rate = (volume_ml * drop_factor_gtts_per_ml) / infusion_time_minutes
        return f"IV drip rate: {drip_rate:.1f} drops/min (gtts/min)."
    except Exception as e:
        return f"Error calculating drip rate: {e}"


@tool
def calculate_bmi(weight_kg: float, height_m: float) -> str:
    """Calculates Body Mass Index (BMI) given weight in kilograms and
    height in metres, and returns the BMI value along with its standard
    WHO classification category."""
    try:
        if weight_kg <= 0:
            return "Error: weight must be greater than zero."
        if height_m <= 0:
            return "Error: height must be greater than zero."

        bmi = weight_kg / (height_m ** 2)

        if bmi < 18.5:
            category = "Underweight"
        elif bmi < 25:
            category = "Normal weight"
        elif bmi < 30:
            category = "Overweight"
        else:
            category = "Obese"

        return f"BMI: {bmi:.1f} ({category})"
    except Exception as e:
        return f"Error calculating BMI: {e}"


# --- Quick standalone tests ---
if __name__ == "__main__":
    print(calculate_medication_dosage.invoke({"patient_weight_kg": 25, "dose_per_kg_mg": 10}))
    print(calculate_iv_drip_rate.invoke({"volume_ml": 1000, "infusion_time_hours": 8}))
    print(calculate_bmi.invoke({"weight_kg": 70, "height_m": 1.75}))

    # --- Error handling tests ---
    print(calculate_medication_dosage.invoke({"patient_weight_kg": 0, "dose_per_kg_mg": 10}))
    print(calculate_bmi.invoke({"weight_kg": 70, "height_m": 0}))