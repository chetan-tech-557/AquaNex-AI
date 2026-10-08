"""Pollution risk prediction combining multi-parameter engine and trained models."""

from typing import Dict, Any
from backend.app.risk.pollution_risk import evaluate_pollution_risk
from backend.app.schemas.prediction_schema import PollutionRiskResult
from backend.app.models.pollution_model import PollutionModelWrapper


class PollutionPredictionService:
    """Predicts aggregate pond pollution risk and generates mitigation guidance."""

    def __init__(self):
        self.ml_wrapper = PollutionModelWrapper()

    def predict_pollution_risk(
        self,
        features: Dict[str, Any],
        feed_kg: float,
        expected_waste_kg: float,
    ) -> PollutionRiskResult:
        """Calculate pollution risk score, classification tier, and remediation advice."""
        # 1. Scientific multi-parameter domain evaluation
        score, level, factors, sub_scores, mitigation = evaluate_pollution_risk(
            features=features,
            feed_kg=feed_kg,
            expected_waste_kg=expected_waste_kg,
        )

        # 2. ML cross-check if model available
        ml_score = self.ml_wrapper.predict_score(features)
        if ml_score is not None:
            # Reconcile if ML predicts heightened risk under adverse conditions
            if ml_score > score:
                score = int(round(0.6 * score + 0.4 * ml_score))
                if score >= 65:
                    level = "HIGH"
                elif score >= 35:
                    level = "MEDIUM"

        return PollutionRiskResult(
            risk_score=score,
            risk_level=level,
            contributing_factors=factors,
            sub_scores=sub_scores,
            recommended_mitigation=mitigation,
        )
