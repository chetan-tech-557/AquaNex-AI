"""Schema definitions for AquaNex AI."""

from backend.app.schemas.input_schema import (
    FishInfo,
    WaterQuality,
    FeedingInfo,
    EnvironmentalInfo,
    FeedingPredictionInput,
)
from backend.app.schemas.prediction_schema import (
    FeedPredictionResult,
    WastePredictionResult,
    PollutionRiskResult,
)
from backend.app.schemas.recommendation_schema import (
    MealScheduleItem,
    BaselineComparison,
    OptimizationResult,
    FeatureContribution,
    ExplanationResult,
    FinalRecommendationResponse,
)

__all__ = [
    "FishInfo",
    "WaterQuality",
    "FeedingInfo",
    "EnvironmentalInfo",
    "FeedingPredictionInput",
    "FeedPredictionResult",
    "WastePredictionResult",
    "PollutionRiskResult",
    "MealScheduleItem",
    "BaselineComparison",
    "OptimizationResult",
    "FeatureContribution",
    "ExplanationResult",
    "FinalRecommendationResponse",
]
