"""Central recommendation service orchestrating the entire AquaNex AI pipeline.

INPUT
↓
VALIDATION
↓
DATA PREPROCESSING & FEATURE ENGINEERING
↓
FEED REQUIREMENT PREDICTION
↓
FEED WASTE PREDICTION
↓
POLLUTION RISK ANALYSIS
↓
OPTIMIZATION
↓
FEEDING SCHEDULE
↓
SHAP / EXPLANATION
↓
DATABASE PERSISTENCE
↓
FINAL RECOMMENDATION
"""

import logging
from typing import Dict, Any, Union

from backend.app.schemas.input_schema import FeedingPredictionInput
from backend.app.schemas.recommendation_schema import FinalRecommendationResponse
from backend.app.data.validation import validate_input_data, ValidationError
from backend.app.data.feature_engineering import engineer_features_from_input, engineer_features_dict
from backend.app.prediction.feed_prediction import FeedPredictionService
from backend.app.prediction.waste_prediction import WastePredictionService
from backend.app.prediction.pollution_prediction import PollutionPredictionService
from backend.app.optimization.optimizer import FeedingOptimizer
from backend.app.explainability.shap_explainer import ShapExplainerService
from backend.app.database.repository import AquacultureRepository

logger = logging.getLogger("RecommendationService")


class AquacultureRecommendationService:
    """Production service coordinating all ML, risk, optimization, explainability, and database tasks."""

    def __init__(self):
        self.feed_service = FeedPredictionService()
        self.waste_service = WastePredictionService()
        self.pollution_service = PollutionPredictionService()
        self.optimizer = FeedingOptimizer()
        self.explainer = ShapExplainerService()
        self.repository = AquacultureRepository()
        self.repository.seed_default_ponds_if_empty()

    def generate_recommendation(
        self,
        input_data: Union[FeedingPredictionInput, Dict[str, Any]],
        persist: bool = True,
    ) -> FinalRecommendationResponse:
        """Execute the end-to-end aquaculture decision support pipeline."""
        # Step 1: Input Parsing & Normalization
        if isinstance(input_data, dict):
            try:
                user_input = FeedingPredictionInput.from_flat_dict(input_data)
            except Exception as exc:
                logger.error("Input parsing failed: %s", exc)
                raise ValidationError(f"Invalid input data format: {exc}") from exc
        elif isinstance(input_data, FeedingPredictionInput):
            user_input = input_data
        else:
            raise ValidationError(f"Unsupported input type '{type(input_data)}'. Must be dict or FeedingPredictionInput.")

        # Step 2: Input Validation
        is_valid, errors, validation_warnings = validate_input_data(user_input)
        if not is_valid:
            error_msg = "; ".join(errors)
            logger.error("Validation rejected input: %s", error_msg)
            raise ValidationError(f"Input validation error: {error_msg}")

        # Step 3: Feature Engineering
        features = engineer_features_from_input(user_input)

        # Step 4: Feed Requirement Prediction (ML + Hypoxia guard)
        feed_pred = self.feed_service.predict_feed_requirement(features)

        # Step 5: Feed Waste Prediction (ML + Waste Risk)
        waste_pred = self.waste_service.predict_waste(
            features=features,
            feed_kg=feed_pred.recommended_daily_feed_kg,
        )

        # Step 6: Pollution Risk Analysis (Multi-parameter Engine)
        pollution_res = self.pollution_service.predict_pollution_risk(
            features=features,
            feed_kg=feed_pred.recommended_daily_feed_kg,
            expected_waste_kg=waste_pred.expected_waste_kg,
        )

        # Step 7: SciPy Optimization & Feeding Schedule
        optimization_res = self.optimizer.optimize_feeding(
            predicted_feed_kg=feed_pred.recommended_daily_feed_kg,
            expected_waste_kg=waste_pred.expected_waste_kg,
            pollution_risk_score=pollution_res.risk_score,
            biomass_kg=user_input.fish.biomass_kg,
            features=features,
        )

        # Step 8: SHAP Explainability
        explanation_res = self.explainer.explain_prediction(
            features=features,
            predicted_feed_kg=feed_pred.recommended_daily_feed_kg,
        )

        # Collect warnings
        warnings = list(validation_warnings)
        if feed_pred.applied_cap:
            warnings.append(feed_pred.applied_cap)

        outside_validated_range = len(validation_warnings) > 0
        reliability = (
            "Caution: Operating near biological stress limits"
            if outside_validated_range
            else "Prediction reliability: Model-based estimate"
        )

        # Step 8.5: Adapt result for direct Next.js frontend consumption
        frontend_result = build_adapted_frontend_result(
            user_input=user_input,
            features=features,
            feed_pred=feed_pred,
            waste_pred=waste_pred,
            pollution_res=pollution_res,
            optimization_res=optimization_res,
            explanation_res=explanation_res,
            raw_data=input_data if isinstance(input_data, dict) else None,
        )

        # Assemble final structured response
        response = FinalRecommendationResponse(
            pond_id=user_input.pond_id or "pond_01",
            feed_prediction=feed_pred,
            waste_prediction=waste_pred,
            pollution_risk=pollution_res,
            optimization=optimization_res,
            explanation=explanation_res,
            warnings=warnings,
            outside_validated_range=outside_validated_range,
            reliability=reliability,
            frontend_feeding_result=frontend_result,
        )

        # Step 9: Database Persistence
        if persist:
            try:
                self.repository.save_recommendation(user_input, response)
            except Exception as db_exc:
                logger.error("Failed to persist recommendation to database: %s", db_exc)

        logger.info(
            "Recommendation complete for pond '%s': Feed %.2f kg (Optimized: %.2f kg, %d meals)",
            response.pond_id,
            feed_pred.recommended_daily_feed_kg,
            optimization_res.optimized_daily_feed_kg,
            optimization_res.number_of_meals,
        )
        return response


def build_adapted_frontend_result(
    user_input: FeedingPredictionInput,
    features: Dict[str, Any],
    feed_pred: FeedPredictionResult,
    waste_pred: WastePredictionResult,
    pollution_res: PollutionRiskResult,
    optimization_res: OptimizationResult,
    explanation_res: ExplanationResult,
    raw_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Format and adapt backend ML & optimization results for direct consumption by Next.js components."""
    data = raw_data or {}
    pond_vol = float(data.get("pondVolume", data.get("pond_volume", 800.0)))
    biomass_kg = round(user_input.fish.biomass_kg, 2)
    stocking_density = round(biomass_kg / max(1.0, pond_vol), 2)

    opt_feed_kg = optimization_res.optimized_daily_feed_kg
    base_comp = optimization_res.baseline_comparison
    base_feed_kg = base_comp.baseline_feed_kg if base_comp else round(biomass_kg * 0.025, 2)
    saved_kg = round(max(0.0, base_feed_kg - opt_feed_kg), 2)
    saved_pct = round((saved_kg / max(0.01, base_feed_kg)) * 100.0, 1)

    # Biological factors calculated by backend
    from backend.app.config.constants import SPECIES_PROFILES
    profile = SPECIES_PROFILES.get(user_input.fish.species, SPECIES_PROFILES["Tilapia"])

    t = user_input.water.water_temperature_c
    opt_t = profile["optimal_temperature_c"]
    temp_dev = abs(t - opt_t)
    temp_factor = round(max(0.0, min(1.0, 1.0 - (temp_dev / 10.0))), 2)

    do = user_input.water.dissolved_oxygen_mg_l
    crit_do = profile["critical_do_mg_l"]
    min_do = profile["min_do_mg_l"]
    if do < crit_do:
        oxygen_factor = 0.0
    elif do >= min_do:
        oxygen_factor = 1.0
    else:
        oxygen_factor = round(0.4 + 0.6 * ((do - crit_do) / max(0.1, min_do - crit_do)), 2)

    amm = user_input.water.ammonia_mg_l
    if amm <= 0.03:
        ammonia_factor = 1.0
    elif amm <= 0.05:
        ammonia_factor = 0.9
    elif amm <= 0.08:
        ammonia_factor = 0.7
    elif amm <= 0.15:
        ammonia_factor = 0.5
    else:
        ammonia_factor = 0.25

    ph = user_input.water.ph
    if ph < 5.0 or ph > 10.0:
        ph_factor = 0.0
    elif ph < 6.5:
        ph_factor = round(0.4 + 0.6 * ((ph - 5.0) / 1.5), 2)
    elif ph <= 8.5:
        ph_factor = 1.0
    else:
        ph_factor = round(max(0.0, 1.0 - 0.6 * ((ph - 8.5) / 1.5)), 2)

    season_str = str(data.get("season", "summer")).lower()
    season_factor = 0.85 if "monsoon" in season_str else (0.80 if "winter" in season_str else (0.95 if "summer" in season_str else 1.0))
    season_window = [8, 17.5] if "monsoon" in season_str else ([9, 16.5] if "winter" in season_str else ([6.5, 18.5] if "summer" in season_str else [7, 18]))

    appetite_index = round(max(0.0, min(1.5, opt_feed_kg / max(0.01, base_feed_kg))), 2)
    suspended = do < crit_do or opt_feed_kg <= 0.01

    protein = 35
    fcr = profile.get("default_fcr", 1.4)
    pellet_mm = "2.0–3.0"
    if "fry" in user_input.fish.growth_stage.lower():
        protein, pellet_mm, fcr = 45, "0.5", 0.9
    elif "juvenile" in user_input.fish.growth_stage.lower():
        protein, pellet_mm, fcr = 38, "1.5–2.0", 1.2
    elif "adult" in user_input.fish.growth_stage.lower():
        protein, pellet_mm, fcr = 30, "4.0–6.0", 1.6

    nitrogen_per_kg = (protein / 100.0) * 0.16
    nitrogen_opt_kg = round(opt_feed_kg * nitrogen_per_kg * (1 - 0.3), 3)
    nitrogen_base_kg = round(nitrogen_opt_kg + saved_kg * 0.85 * nitrogen_per_kg, 3)
    phosphorus_opt_kg = round(opt_feed_kg * 0.01 * (1 - 0.3), 3)
    expected_gain_kg = round(opt_feed_kg / max(0.1, fcr), 2)

    # Format meals for Next.js ScheduleTable and FeedTimer
    meals_out = []
    total_opt = max(0.01, opt_feed_kg)
    for idx, m in enumerate(optimization_res.meal_schedule):
        # Convert "08:00 AM" or "01:00 PM" to decimal hour
        t_str = m.time
        hour_dec = 8.0
        try:
            parts = t_str.split()
            h_m = parts[0].split(":")
            h_val = float(h_m[0])
            m_val = float(h_m[1]) if len(h_m) > 1 else 0.0
            if len(parts) > 1 and parts[1].upper() == "PM" and h_val < 12:
                h_val += 12.0
            elif len(parts) > 1 and parts[1].upper() == "AM" and h_val == 12:
                h_val = 0.0
            hour_dec = h_val + (m_val / 60.0)
        except Exception:
            hour_dec = 8.0 + idx * 4.0

        share = m.quantity_kg / total_opt
        note = "peak" if idx == 1 or idx == len(optimization_res.meal_schedule) // 2 else ("taper" if idx == len(optimization_res.meal_schedule) - 1 else "steady")

        # 24h formatted time "08:00"
        h_int = int(hour_dec)
        m_int = int(round((hour_dec - h_int) * 60.0))
        fmt_24 = f"{h_int:02d}:{m_int:02d}"

        meals_out.append({
            "hour": hour_dec,
            "time": fmt_24,
            "grams": round(m.quantity_kg * 1000.0, 1),
            "share": round(share, 3),
            "note": note,
        })

    # 7-day projection
    projection = []
    cur_w = user_input.fish.average_fish_weight_g
    live_count = user_input.fish.fish_count or max(1, int(round((biomass_kg * 1000.0) / max(0.1, cur_w))))
    for day in range(1, 8):
        day_bio = (live_count * cur_w) / 1000.0
        day_feed = round(opt_feed_kg * (1.0 + 0.02 * (day - 1)), 2)
        projection.append({
            "day": day,
            "avgWeight": round(cur_w, 1),
            "biomassKg": round(day_bio, 1),
            "feedKg": day_feed,
        })
        gain = ((day_feed / max(0.1, fcr)) * 1000.0) / max(1, live_count)
        cur_w += gain

    # Frontend Alerts translation
    alerts = []
    if do < crit_do:
        alerts.append({
            "level": "critical",
            "id": "doCritical",
            "params": {"oxygen": f"{do:.1f}", "critical": crit_do},
        })
    elif do < min_do:
        alerts.append({
            "level": "warning",
            "id": "doLow",
            "params": {"pct": f"{int(oxygen_factor * 100)}", "optimal": min_do},
        })

    raw_tan = float(data.get("ammonia", data.get("tan", amm / 0.08 if amm < 0.25 else amm)))
    if amm > 0.08 or raw_tan > 2.0:
        alerts.append({
            "level": "critical",
            "id": "ammonia",
            "params": {"tan": f"{raw_tan:.2f}"},
        })
    elif amm > 0.04 or raw_tan > 1.0:
        alerts.append({
            "level": "warning",
            "id": "ammonia",
            "params": {"tan": f"{raw_tan:.2f}"},
        })

    if ph < 5.0 or ph > 10.0:
        alerts.append({
            "level": "critical",
            "id": "phLethal",
            "params": {"ph": f"{ph:.1f}"},
        })
    elif ph < 6.5 or ph > 8.5:
        alerts.append({
            "level": "warning",
            "id": "phAcidic" if ph < 6.5 else "phAlkaline",
            "params": {"pct": f"{int(ph_factor * 100)}", "toxic": ph > 8.5 and amm > 0.03},
        })

    if not alerts:
        alerts.append({
            "level": "info",
            "id": "optimal",
            "params": {},
        })

    return {
        "biomassKg": biomass_kg,
        "stockingDensity": stocking_density,
        "baseFeedKg": base_feed_kg,
        "optimizedFeedKg": opt_feed_kg,
        "savedKg": saved_kg,
        "savedPct": saved_pct,
        "tempFactor": temp_factor,
        "oxygenFactor": oxygen_factor,
        "ammoniaFactor": ammonia_factor,
        "phFactor": ph_factor,
        "seasonFactor": season_factor,
        "feedingWindow": season_window,
        "appetiteIndex": appetite_index,
        "protein": protein,
        "fcr": fcr,
        "pelletMm": pellet_mm,
        "expectedGainKg": expected_gain_kg,
        "nitrogenBaseKg": nitrogen_base_kg,
        "nitrogenOptKg": nitrogen_opt_kg,
        "phosphorusOptKg": phosphorus_opt_kg,
        "meals": meals_out,
        "projection": projection,
        "alerts": alerts,
        "suspended": suspended,
        # AI diagnostics
        "feedPredictionKg": feed_pred.recommended_daily_feed_kg,
        "wastePredictionKg": waste_pred.expected_waste_kg,
        "wasteRiskLevel": waste_pred.risk_level,
        "wasteRiskScore": waste_pred.risk_score,
        "pollutionRiskScore": pollution_res.risk_score,
        "pollutionRiskLevel": pollution_res.risk_level,
        "contributingFactors": pollution_res.contributing_factors,
        "recommendedMitigation": pollution_res.recommended_mitigation,
        "explanationSummary": explanation_res.summary,
        "topFeatures": [f.model_dump() for f in explanation_res.top_features],
        "solverStatus": optimization_res.solver_status,
        "modelName": feed_pred.model_name,
    }


# Singleton service instance for streamlined import across app and frontend
recommendation_service = AquacultureRecommendationService()


def get_recommendation(
    input_data: Union[FeedingPredictionInput, Dict[str, Any]],
    persist: bool = True,
) -> FinalRecommendationResponse:
    """Convenience functional interface for Streamlit and external modules."""
    return recommendation_service.generate_recommendation(input_data=input_data, persist=persist)
