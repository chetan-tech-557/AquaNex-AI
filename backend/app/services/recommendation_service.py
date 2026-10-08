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


# Singleton service instance for streamlined import across app and frontend
recommendation_service = AquacultureRecommendationService()


def get_recommendation(
    input_data: Union[FeedingPredictionInput, Dict[str, Any]],
    persist: bool = True,
) -> FinalRecommendationResponse:
    """Convenience functional interface for Streamlit and external modules."""
    return recommendation_service.generate_recommendation(input_data=input_data, persist=persist)
