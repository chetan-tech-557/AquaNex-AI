"""Feed waste prediction module combining ML estimation and diagnostic risk scoring."""

from typing import Dict, Any
from backend.app.models.waste_model import WasteModelWrapper
from backend.app.risk.waste_risk import evaluate_waste_risk
from backend.app.schemas.prediction_schema import WastePredictionResult


class WastePredictionService:
    """Predicts expected uneaten feed in kg and categorizes risk."""

    def __init__(self):
        self.model_wrapper = WasteModelWrapper()

    def predict_waste(
        self,
        features: Dict[str, Any],
        feed_kg: float,
    ) -> WastePredictionResult:
        """Estimate uneaten feed waste and assign risk level."""
        # Use ML model to estimate waste
        raw_waste_kg = self.model_wrapper.predict(features)

        # Scale waste proportionally if feed_kg was adjusted by optimizer or caps
        prev_feed = float(features.get("previousFeedKg", 5.0))
        if prev_feed > 0:
            feed_scale = feed_kg / max(0.5, prev_feed)
            expected_waste_kg = max(0.05, raw_waste_kg * np_sqrt_scale(feed_scale))
        else:
            expected_waste_kg = max(0.05, raw_waste_kg)

        # Waste cannot exceed fed quantity
        expected_waste_kg = min(expected_waste_kg, feed_kg * 0.45)
        waste_pct = (expected_waste_kg / max(0.01, feed_kg)) * 100.0

        risk_score, risk_level, reasons = evaluate_waste_risk(
            feed_kg=feed_kg,
            expected_waste_kg=expected_waste_kg,
            features=features,
        )

        return WastePredictionResult(
            expected_waste_kg=round(expected_waste_kg, 2),
            waste_percentage=round(waste_pct, 1),
            risk_level=risk_level,
            risk_score=risk_score,
            contributing_reasons=reasons,
        )


def np_sqrt_scale(val: float) -> float:
    import math
    return math.sqrt(max(0.1, val))
