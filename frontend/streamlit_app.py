import streamlit as st
import sys
import os

# Ensure backend directory is accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.calculator import (
    calculate_tdd,
    calculate_correction_scale,
    evaluate_blood_glucose,
)

st.set_page_config(
    page_title="GlycoGuard | Inpatient Glycemic Protocol CDSS",
    page_icon="💉",
    layout="wide",
)

st.title("💉 GlycoGuard: Inpatient Basal-Bolus & Correctional Insulin Engine")
st.caption(
    "Clinical Decision Support System (CDSS) for inpatient glycemic control aligned with ADA/Endocrine Society guidelines."
)

st.divider()

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Patient Clinical Parameters")
    weight_kg = st.number_input(
        "Patient Weight (kg)", min_value=30.0, max_value=250.0, value=75.0, step=0.5
    )

    scenario_label = st.selectbox(
        "Clinical Scenario & Risk Profile",
        options=[
            "Conservative / Renal Impairment / Elderly (0.3 U/kg)",
            "Standard Inpatient / Insulin-Naive (0.45 U/kg)",
            "Severe Insulin Resistance / Systemic Corticosteroids (0.6 U/kg)",
        ],
        index=1,
    )

    scenario_map = {
        "Conservative / Renal Impairment / Elderly (0.3 U/kg)": "conservative",
        "Standard Inpatient / Insulin-Naive (0.45 U/kg)": "standard",
        "Severe Insulin Resistance / Systemic Corticosteroids (0.6 U/kg)": "resistant",
    }
    selected_scenario = scenario_map[scenario_label]

    st.subheader("Point-of-Care Acute Glucose")
    current_bg = st.number_input(
        "Current Capillary Blood Glucose (mg/dL)",
        min_value=30,
        max_value=600,
        value=185,
        step=1,
    )
    target_bg = st.number_input(
        "Target Blood Glucose (mg/dL)",
        min_value=100,
        max_value=180,
        value=140,
        step=5,
    )

    evaluate_btn = st.button("Calculate Protocol & Orders", type="primary")

with col2:
    st.subheader("Clinical Orders & Dosing Recommendations")

    if evaluate_btn or True:
        tdd_data = calculate_tdd(weight_kg, selected_scenario)
        correction_data = calculate_correction_scale(tdd_data["tdd_units"], target_bg)
        eval_result = evaluate_blood_glucose(
            current_bg, tdd_data["tdd_units"], target_bg
        )

        # Blood Glucose Alert Card
        if eval_result["status"] == "CRITICAL_HYPO":
            st.error(f"🚨 **{eval_result['alert']}**")
            st.error(eval_result["action"])
        elif eval_result["status"] == "HYPERGLYCEMIC":
            st.warning(f"⚠️ **{eval_result['alert']}**")
            st.info(eval_result["action"])
        else:
            st.success(f"✅ **{eval_result['alert']}**")
            st.write(eval_result["action"])

        st.markdown("### 1. Basal-Bolus Regimen (50/50 Split)")
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Daily Dose (TDD)", f"{tdd_data['tdd_units']} units")
        m2.metric("Basal (Glargine/Degludec)", f"{tdd_data['basal_daily_units']} units/day")
        m3.metric("Prandial (Lispro/Aspart)", f"{tdd_data['prandial_meal_units']} units / meal")

        st.caption("Prandial dose divided equally across Breakfast, Lunch, and Dinner.")

        st.markdown("### 2. Personalized Correctional Sliding Scale")
        st.write(f"**Insulin Sensitivity Factor (ISF):** 1 unit drops blood glucose by ~**{correction_data['isf_mg_dl']} mg/dL** (Rule of 1800)")

        # Render scale table
        scale_rows = [
            {"Blood Glucose Range (mg/dL)": row["bg_range"], "Rapid-Acting Insulin": f"+{row['correction_units']} units"}
            for row in correction_data["scale"]
        ]
        st.table(scale_rows)

st.divider()
st.caption("GlycoGuard CDSS | Open Source Pharmacotherapy Project | Developer: Amrutha Nandini")