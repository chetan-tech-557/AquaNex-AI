"""Streamlit Frontend Application for AquaNex AI.

Connects directly to the backend recommendation service:
`from backend.app.services.recommendation_service import get_recommendation`
"""

import sys
from pathlib import Path
import json

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
import numpy as np

from backend.app.services.recommendation_service import get_recommendation
from backend.app.database.repository import AquacultureRepository
from backend.app.config.constants import (
    DATASET_LABEL,
    DATASET_DISCLAIMER,
    SUPPORTED_SPECIES,
    SUPPORTED_GROWTH_STAGES,
)
from backend.app.config.settings import settings

st.set_page_config(
    page_title="AquaNex AI — Aquaculture Feeding Optimization",
    page_icon="🐟",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for clean aesthetics
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0E7490;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.2rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 14px;
        text-align: center;
    }
    .risk-badge-low {
        background-color: #DCFCE7;
        color: #166534;
        font-weight: bold;
        padding: 4px 10px;
        border-radius: 6px;
    }
    .risk-badge-med {
        background-color: #FEF08A;
        color: #854D0E;
        font-weight: bold;
        padding: 4px 10px;
        border-radius: 6px;
    }
    .risk-badge-high {
        background-color: #FEE2E2;
        color: #991B1B;
        font-weight: bold;
        padding: 4px 10px;
        border-radius: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Repository for history
repo = AquacultureRepository()

# --- PRESET SCENARIOS ---
SCENARIOS = {
    "Scenario 1: Normal Pond": {
        "species": "Tilapia",
        "growth_stage": "Grow-out",
        "fish_age_days": 190,
        "biomass_kg": 250.0,
        "average_fish_weight_g": 150.0,
        "water_temperature_c": 27.0,
        "dissolved_oxygen_mg_l": 6.2,
        "ph": 7.4,
        "ammonia_mg_l": 0.025,
        "nitrate_mg_l": 22.0,
        "turbidity": 14.0,
        "salinity_ppt": 0.5,
        "previous_feed_kg": 5.0,
        "recent_average_feed_kg": 5.2,
        "feeding_frequency": 2,
        "feed_quality_score": 82.0,
        "rainfall_mm": 8.0,
        "humidity_percent": 66.0,
        "air_temperature_c": 25.5,
    },
    "Scenario 2: Low Dissolved Oxygen": {
        "species": "Tilapia",
        "growth_stage": "Grow-out",
        "fish_age_days": 190,
        "biomass_kg": 250.0,
        "average_fish_weight_g": 150.0,
        "water_temperature_c": 27.0,
        "dissolved_oxygen_mg_l": 2.7,
        "ph": 7.4,
        "ammonia_mg_l": 0.065,
        "nitrate_mg_l": 22.0,
        "turbidity": 14.0,
        "salinity_ppt": 0.5,
        "previous_feed_kg": 5.0,
        "recent_average_feed_kg": 5.2,
        "feeding_frequency": 2,
        "feed_quality_score": 82.0,
        "rainfall_mm": 8.0,
        "humidity_percent": 66.0,
        "air_temperature_c": 25.5,
    },
    "Scenario 3: High Toxic Ammonia": {
        "species": "Tilapia",
        "growth_stage": "Grow-out",
        "fish_age_days": 190,
        "biomass_kg": 250.0,
        "average_fish_weight_g": 150.0,
        "water_temperature_c": 27.0,
        "dissolved_oxygen_mg_l": 5.5,
        "ph": 7.9,
        "ammonia_mg_l": 0.12,
        "nitrate_mg_l": 48.0,
        "turbidityNtu": 18.0,
        "salinity_ppt": 0.5,
        "previous_feed_kg": 5.0,
        "recent_average_feed_kg": 5.2,
        "feeding_frequency": 2,
        "feed_quality_score": 82.0,
        "rainfall_mm": 8.0,
        "humidity_percent": 66.0,
        "air_temperature_c": 25.5,
    },
    "Scenario 4: High Turbidity & Runoff": {
        "species": "Tilapia",
        "growth_stage": "Grow-out",
        "fish_age_days": 190,
        "biomass_kg": 250.0,
        "average_fish_weight_g": 150.0,
        "water_temperature_c": 27.0,
        "dissolved_oxygen_mg_l": 5.2,
        "ph": 7.4,
        "ammonia_mg_l": 0.035,
        "nitrate_mg_l": 35.0,
        "turbidity": 68.0,
        "salinity_ppt": 0.5,
        "previous_feed_kg": 5.0,
        "recent_average_feed_kg": 5.2,
        "feeding_frequency": 2,
        "feed_quality_score": 82.0,
        "rainfall_mm": 85.0,
        "humidity_percent": 82.0,
        "air_temperature_c": 25.5,
    },
    "Scenario 5: Mature Adult Fish": {
        "species": "Tilapia",
        "growth_stage": "Adult",
        "fish_age_days": 550,
        "biomass_kg": 250.0,
        "average_fish_weight_g": 650.0,
        "water_temperature_c": 27.0,
        "dissolved_oxygen_mg_l": 6.2,
        "ph": 7.4,
        "ammonia_mg_l": 0.025,
        "nitrate_mg_l": 22.0,
        "turbidity": 14.0,
        "salinity_ppt": 0.5,
        "previous_feed_kg": 4.2,
        "recent_average_feed_kg": 4.3,
        "feeding_frequency": 2,
        "feed_quality_score": 82.0,
        "rainfall_mm": 8.0,
        "humidity_percent": 66.0,
        "air_temperature_c": 25.5,
    },
    "Scenario 6: High Stock Biomass": {
        "species": "Tilapia",
        "growth_stage": "Adult",
        "fish_age_days": 340,
        "biomass_kg": 720.0,
        "average_fish_weight_g": 780.0,
        "water_temperature_c": 28.0,
        "dissolved_oxygen_mg_l": 6.7,
        "ph": 7.4,
        "ammonia_mg_l": 0.025,
        "nitrate_mg_l": 22.0,
        "turbidity": 14.0,
        "salinity_ppt": 0.5,
        "previous_feed_kg": 8.0,
        "recent_average_feed_kg": 7.7,
        "feeding_frequency": 3,
        "feed_quality_score": 82.0,
        "rainfall_mm": 8.0,
        "humidity_percent": 66.0,
        "air_temperature_c": 25.5,
    },
}

# --- SIDEBAR: INPUT CONTROLS ---
with st.sidebar:
    st.image(
        "https://raw.githubusercontent.com/chetan-tech-557/AquaNex-AI/main/logo.png" if False else "https://img.icons8.com/fluency/96/aquarium.png",
        width=64,
    )
    st.title("AquaNex AI")
    st.caption("Aarambh WCE Hackathon 2026")

    # Pond Selection
    ponds_list = repo.list_ponds()
    pond_options = {p["pond_id"]: f"{p['name']} ({p['pond_id']})" for p in ponds_list} if ponds_list else {"pond_01": "Pond 1"}
    selected_pond_id = st.selectbox("Select Pond", options=list(pond_options.keys()), format_func=lambda x: pond_options[x])

    st.markdown("---")
    st.subheader("Demo Scenarios")
    scenario_choice = st.selectbox("Load Test Scenario", ["Custom (Manual Input)"] + list(SCENARIOS.keys()))

    if scenario_choice != "Custom (Manual Input)":
        defaults = SCENARIOS[scenario_choice]
    else:
        defaults = SCENARIOS["Scenario 1: Normal Pond"]

    st.markdown("---")
    st.subheader("Pond & Fish Inputs")

    species_idx = SUPPORTED_SPECIES.index(defaults["species"]) if defaults["species"] in SUPPORTED_SPECIES else 0
    species = st.selectbox("Fish Species", SUPPORTED_SPECIES, index=species_idx)

    stage_idx = SUPPORTED_GROWTH_STAGES.index(defaults["growth_stage"]) if defaults["growth_stage"] in SUPPORTED_GROWTH_STAGES else 2
    growth_stage = st.selectbox("Growth Stage", SUPPORTED_GROWTH_STAGES, index=stage_idx)

    col_a, col_b = st.columns(2)
    with col_a:
        biomass_kg = st.number_input("Biomass (kg)", min_value=1.0, max_value=10000.0, value=float(defaults["biomass_kg"]), step=10.0)
        fish_age = st.number_input("Age (Days)", min_value=1, max_value=2000, value=int(defaults["fish_age_days"]))
    with col_b:
        avg_weight_g = st.number_input("Avg Weight (g)", min_value=1.0, max_value=5000.0, value=float(defaults["average_fish_weight_g"]), step=10.0)
        fish_count = max(1, int(round((biomass_kg * 1000.0) / max(1.0, avg_weight_g))))
        st.metric("Fish Count (est.)", f"{fish_count:,}")

    st.markdown("---")
    st.subheader("Water Quality Parameters")
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        water_temp = st.number_input("Temp (°C)", min_value=4.0, max_value=40.0, value=float(defaults["water_temperature_c"]), step=0.5)
        do_val = st.number_input("Dissolved O₂ (mg/L)", min_value=0.5, max_value=15.0, value=float(defaults["dissolved_oxygen_mg_l"]), step=0.1)
        ph_val = st.number_input("pH", min_value=4.5, max_value=10.0, value=float(defaults["ph"]), step=0.1)
    with col_w2:
        ammonia_val = st.number_input("Ammonia (mg/L)", min_value=0.0, max_value=1.5, value=float(defaults["ammonia_mg_l"]), step=0.005, format="%.3f")
        turbidity_val = st.number_input("Turbidity (NTU)", min_value=0.0, max_value=200.0, value=float(defaults.get("turbidity", 14.0)), step=1.0)
        nitrate_val = st.number_input("Nitrate (mg/L)", min_value=0.0, max_value=150.0, value=float(defaults["nitrate_mg_l"]), step=2.0)

    st.markdown("---")
    st.subheader("Feeding & Weather")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        prev_feed = st.number_input("Prior Day Feed (kg)", min_value=0.0, max_value=500.0, value=float(defaults["previous_feed_kg"]), step=0.5)
        meals_day = st.slider("Meals/Day", min_value=1, max_value=5, value=int(defaults["feeding_frequency"]))
    with col_f2:
        feed_quality = st.slider("Feed Quality Index", min_value=20, max_value=100, value=int(defaults["feed_quality_score"]))
        recent_avg = st.number_input("Recent Avg Feed (kg)", min_value=0.0, max_value=500.0, value=float(defaults["recent_average_feed_kg"]), step=0.5)

    rainfall_val = st.number_input("Rainfall (mm/day)", min_value=0.0, max_value=300.0, value=float(defaults["rainfall_mm"]), step=5.0)

    execute_btn = st.button("🚀 Calculate Optimized Feeding", type="primary", use_container_width=True)

# Build payload
current_input = {
    "pond_id": selected_pond_id,
    "species": species,
    "growth_stage": growth_stage,
    "fish_age_days": fish_age,
    "biomass_kg": biomass_kg,
    "average_fish_weight_g": avg_weight_g,
    "fish_count": fish_count,
    "water_temperature_c": water_temp,
    "dissolved_oxygen_mg_l": do_val,
    "ph": ph_val,
    "ammonia_mg_l": ammonia_val,
    "nitrate_mg_l": nitrate_val,
    "turbidity": turbidity_val,
    "salinity_ppt": float(defaults.get("salinity_ppt", 0.5)),
    "previous_feed_kg": prev_feed,
    "recent_average_feed_kg": recent_avg,
    "feeding_frequency": meals_day,
    "feed_quality_score": feed_quality,
    "rainfall_mm": rainfall_val,
    "humidity_percent": float(defaults.get("humidity_percent", 66.0)),
    "air_temperature_c": float(defaults.get("air_temperature_c", 25.5)),
}

# --- MAIN DASHBOARD AREA ---
st.markdown("<div class='main-title'>AquaNex AI — Adaptive Aquaculture Feeding</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='sub-title'>AI-Driven Feed Optimization, Waste Reduction & Pollution Risk Management | <i>Aarambh WCE Hackathon 2026</i></div>",
    unsafe_allow_html=True,
)

# Run recommendation pipeline
with st.spinner("Executing ML pipeline, SciPy optimization, and SHAP explainability..."):
    rec = get_recommendation(current_input, persist=execute_btn)

# Show warnings if any
if rec.warnings:
    for w in rec.warnings:
        if "CRITICAL" in w or "hypoxia" in w.lower():
            st.error(f"⚠️ {w}")
        else:
            st.warning(f"ℹ️ {w}")

# Top Metric KPI Row
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
with kpi1:
    st.metric(
        label="Predicted Daily Appetite",
        value=f"{rec.feed_prediction.recommended_daily_feed_kg:.2f} kg",
        help=f"Model: {rec.feed_prediction.model_name}",
    )
with kpi2:
    st.metric(
        label="SciPy Optimized Feed",
        value=f"{rec.optimization.optimized_daily_feed_kg:.2f} kg",
        delta=f"{rec.optimization.number_of_meals} meals/day",
    )
with kpi3:
    w_level = rec.waste_prediction.risk_level
    st.metric(
        label=f"Expected Waste ({w_level})",
        value=f"{rec.waste_prediction.expected_waste_kg:.2f} kg",
        delta=f"Risk Score: {rec.waste_prediction.risk_score}/100",
        delta_color="inverse",
    )
with kpi4:
    p_level = rec.pollution_risk.risk_level
    st.metric(
        label=f"Pollution Risk ({p_level})",
        value=f"{rec.pollution_risk.risk_score}/100",
        delta=p_level,
        delta_color="inverse",
    )
with kpi5:
    if rec.optimization.baseline_comparison:
        saved_cost = rec.optimization.baseline_comparison.cost_saved_usd
        st.metric(
            label="Daily Cost Savings",
            value=f"${saved_cost:.2f}",
            delta=f"-{rec.optimization.baseline_comparison.feed_saved_kg:.2f} kg feed",
        )
    else:
        st.metric(label="Daily Cost", value=f"${rec.optimization.estimated_daily_cost:.2f}")

st.markdown("---")

# Main Content Tabs
tab_sched, tab_shap, tab_risk, tab_hist, tab_method = st.tabs([
    "📅 Feeding Schedule & Optimization",
    "🧠 Explainable AI (SHAP)",
    "🧪 Water Chemistry & Risk",
    "📜 Historical Pond Records",
    "📚 Methodology & Models",
])

# TAB 1: Feeding Schedule & Optimization
with tab_sched:
    st.subheader("Optimal Feeding Schedule")
    col_t1, col_t2 = st.columns([3, 2])

    with col_t1:
        st.markdown(f"**Recommended Distribution ({rec.optimization.number_of_meals} Meals/Day)**")
        sched_data = [
            {"Meal #": m.meal_number, "Feeding Time": m.time, "Ration (kg)": f"{m.quantity_kg:.2f} kg"}
            for m in rec.optimization.meal_schedule
        ]
        st.table(pd.DataFrame(sched_data))

    with col_t2:
        st.markdown("**Comparison vs Static Feeding Chart Baseline**")
        if rec.optimization.baseline_comparison:
            b = rec.optimization.baseline_comparison
            comp_df = pd.DataFrame([
                {"Metric": "Daily Feed Quantity", "Static Chart": f"{b.baseline_feed_kg:.2f} kg", "AquaNex AI": f"{rec.optimization.optimized_daily_feed_kg:.2f} kg", "Benefit": f"-{b.feed_saved_kg:.2f} kg"},
                {"Metric": "Estimated Waste", "Static Chart": f"{b.baseline_waste_kg:.2f} kg", "AquaNex AI": f"{rec.waste_prediction.expected_waste_kg:.2f} kg", "Benefit": f"-{b.waste_prevented_kg:.2f} kg"},
                {"Metric": "Daily Feed Cost", "Static Chart": f"${b.baseline_daily_cost:.2f}", "AquaNex AI": f"${rec.optimization.estimated_daily_cost:.2f}", "Benefit": f"${b.cost_saved_usd:.2f} saved"},
                {"Metric": "Pollution Risk Tier", "Static Chart": b.baseline_pollution_risk, "AquaNex AI": rec.pollution_risk.risk_level, "Benefit": "Controlled"},
            ])
            st.table(comp_df)

# TAB 2: Explainable AI (SHAP)
with tab_shap:
    st.subheader("Why did the model produce this recommendation?")
    st.info(rec.explanation.summary)

    if rec.explanation.top_features:
        feat_df = pd.DataFrame([
            {
                "Factor": f.display_name,
                "Observed Input": str(f.value),
                "SHAP Impact (kg)": f.shap_value,
                "Direction": f.impact_direction,
            }
            for f in rec.explanation.top_features
        ])
        st.dataframe(feat_df, use_container_width=True)

        # Plot SHAP bar chart
        chart_data = pd.DataFrame({
            "Feature": [f.display_name for f in rec.explanation.top_features],
            "SHAP Value": [f.shap_value for f in rec.explanation.top_features],
        }).set_index("Feature")
        st.bar_chart(chart_data)

    st.markdown("**Operational Factors:**")
    for bp in rec.explanation.bullet_points:
        st.write(f"- {bp}")

# TAB 3: Water Chemistry & Risk
with tab_risk:
    st.subheader("Multi-Parameter Water & Pollution Risk Breakdown")

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("**Component Risk Sub-scores (0-100)**")
        sub_scores = rec.pollution_risk.sub_scores
        for k, v in sub_scores.items():
            label = k.replace("_", " ").title()
            st.write(f"**{label}**: {v:.1f}/100")
            st.progress(min(1.0, v / 100.0))

    with col_r2:
        st.markdown("**Identified Contributing Stress Factors**")
        for factor in rec.pollution_risk.contributing_factors:
            st.write(f"• {factor}")

        st.markdown("**Recommended Operational Intervention**")
        st.success(rec.pollution_risk.recommended_mitigation)

# TAB 4: Historical Pond Records
with tab_hist:
    st.subheader(f"Historical Records for {selected_pond_id}")
    history = repo.get_pond_history(selected_pond_id, limit=10)
    if history:
        hist_table = []
        for h in history:
            hist_table.append({
                "Timestamp": h.get("recorded_at", "N/A"),
                "Optimized Feed (kg)": h.get("optimized_feed_kg", 0.0),
                "Waste (kg)": h.get("expected_waste_kg", 0.0),
                "Waste Score": h.get("waste_risk_score", 0),
                "Pollution Score": h.get("pollution_risk_score", 0),
                "Meals": h.get("number_of_meals", 0),
                "Cost Saved ($)": h.get("cost_saved_usd", 0.0),
            })
        st.dataframe(pd.DataFrame(hist_table), use_container_width=True)
    else:
        st.write("No prior records logged for this pond.")

# TAB 5: Methodology & Models
with tab_method:
    st.subheader("Scientific Methodology & Technical Specifications")

    st.markdown(f"**Dataset Specification:** `{DATASET_LABEL}`")
    st.caption(DATASET_DISCLAIMER)

    # Load metrics from file if available
    metrics_path = settings.model_metrics_path
    if metrics_path.exists():
        with open(metrics_path, "r") as f:
            metrics_data = json.load(f)
        st.markdown(f"**Champion ML Model:** {metrics_data.get('selectedModel', 'N/A')}")
        st.markdown(f"**Training Rows:** {metrics_data.get('trainingRows')} | **Held-Out Test Rows:** {metrics_data.get('testRows')}")

        st.markdown("**Model Evaluation Comparison:**")
        scores_df = pd.DataFrame(metrics_data.get("modelScores", []))
        st.dataframe(scores_df, use_container_width=True)

    st.markdown(
        """
        **SciPy Constrained Optimization Objective Formulation:**
        $$\\min_{F, M} \\left[ C_{\\text{feed}} \\cdot F + C_{\\text{waste}} \\cdot W(F, M) + \\lambda_{\\text{poll}} \\cdot P(F) + \\mu_{\\text{meal}} \\cdot (M - 1) \\right]$$
        Subject to:
        - $F_{\\min} \\ge 0.70 \\cdot F_{\\text{appetite}}$ (Fish welfare & maintenance requirement)
        - $F_{\\max} \\le 1.25 \\cdot F_{\\text{appetite}}$ (Biological gut ceiling & overfeeding cap)
        - Hypoxia Emergency Bound: $F_{\\max} \\le 0.50 \\cdot F_{\\text{appetite}}$ when $\\text{DO} < 3.0$ mg/L
        """
    )
