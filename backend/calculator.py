"""
GlycoGuard - Inpatient Basal-Bolus & Correctional Insulin Calculation Engine
Based on ADA/Endocrine Society Guidelines for Inpatient Glycemic Management.
"""

def calculate_tdd(weight_kg: float, clinical_scenario: str) -> dict:
    multipliers = {
        "conservative": 0.3,
        "standard": 0.45,
        "resistant": 0.6
    }
    
    factor = multipliers.get(clinical_scenario.lower(), 0.45)
    tdd = round(weight_kg * factor)
    
    basal_total = round(tdd * 0.5)
    prandial_total = tdd - basal_total
    meal_dose = round(prandial_total / 3)
    
    return {
        "tdd_units": tdd,
        "factor_used": factor,
        "basal_daily_units": basal_total,
        "prandial_meal_units": meal_dose,
        "prandial_daily_total": meal_dose * 3
    }


def calculate_correction_scale(tdd_units: int, target_bg: int = 140) -> dict:
    isf = round(1800 / tdd_units) if tdd_units > 0 else 50
    
    scale = [
        {"bg_range": f"{target_bg + 1} - {target_bg + isf}", "correction_units": 1},
        {"bg_range": f"{target_bg + isf + 1} - {target_bg + (2 * isf)}", "correction_units": 2},
        {"bg_range": f"{target_bg + (2 * isf) + 1} - {target_bg + (3 * isf)}", "correction_units": 3},
        {"bg_range": f"> {target_bg + (3 * isf)}", "correction_units": 4}
    ]
    
    return {
        "isf_mg_dl": isf,
        "target_bg": target_bg,
        "scale": scale
    }


def evaluate_blood_glucose(current_bg: int, tdd_units: int, target_bg: int = 140) -> dict:
    if current_bg < 70:
        return {
            "status": "CRITICAL_HYPO",
            "alert": "Severe Hypoglycemia Protocol Triggered",
            "recommended_correction": 0,
            "action": "Hold all insulin. Administer 15g fast-acting oral carbohydrates (or 25mL 50% Dextrose IV if NPO). Recheck in 15 minutes."
        }
    elif current_bg <= target_bg:
        return {
            "status": "EUGLYCEMIC",
            "alert": "Within Target Range",
            "recommended_correction": 0,
            "action": "Administer scheduled basal/prandial dose if eating. No correction required."
        }
    else:
        isf = round(1800 / tdd_units) if tdd_units > 0 else 50
        excess_bg = current_bg - target_bg
        correction_units = round(excess_bg / isf)
        
        return {
            "status": "HYPERGLYCEMIC",
            "alert": "Correction Dose Needed",
            "recommended_correction": max(1, correction_units),
            "action": f"Administer {max(1, correction_units)} unit(s) of rapid-acting insulin with meal dose."
        }