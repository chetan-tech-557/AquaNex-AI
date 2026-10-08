"""Waste model wrapper encapsulating inference and pipeline application."""

from typing import Dict, Any
from backend.app.models.model_loader import get_waste_model, get_feed_pipeline


class WasteModelWrapper:
    """Wrapper around trained feed waste regressor."""

    def __init__(self):
        self._model = None
        self._pipeline = None

    @property
    def model(self):
        if self._model is None:
            self._model = get_waste_model()
        return self._model

    @property
    def pipeline(self):
        if self._pipeline is None:
            self._pipeline = get_feed_pipeline()
        return self._pipeline

    def predict(self, engineered_feature_dict: Dict[str, Any]) -> float:
        """Predict expected uneaten feed in kilograms."""
        X_vec = self.pipeline.transform([engineered_feature_dict])
        pred = float(self.model.predict(X_vec)[0])
        return max(0.0, pred)
