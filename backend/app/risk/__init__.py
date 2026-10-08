"""Risk evaluation package for AquaNex AI."""

from backend.app.risk.waste_risk import evaluate_waste_risk
from backend.app.risk.pollution_risk import evaluate_pollution_risk

__all__ = [
    "evaluate_waste_risk",
    "evaluate_pollution_risk",
]
