"""Prediction package for AquaNex AI."""

from backend.app.prediction.feed_prediction import FeedPredictionService
from backend.app.prediction.waste_prediction import WastePredictionService
from backend.app.prediction.pollution_prediction import PollutionPredictionService

__all__ = [
    "FeedPredictionService",
    "WastePredictionService",
    "PollutionPredictionService",
]
