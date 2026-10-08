"""Pollution model wrapper encapsulating ML score prediction."""

from typing import Dict, Any, Optional
from backend.app.models.model_loader import get_pollution_model, get_feed_pipeline


class PollutionModelWrapper:
    """Wrapper around trained pollution risk scoring model."""

    def __init__(self):
        self._model = None
        self._pipeline = None

    @property
    def model(self):
        if self._model is None:
            self._model = get_pollution_model()
        return self._model

    @property
    def pipeline(self):
        if self._pipeline is None:
            self._pipeline = get_feed_pipeline()
        return self._pipeline

    def predict_score(self, engineered_feature_dict: Dict[str, Any]) -> Optional[float]:
        """Predict continuous pollution risk score if model is available."""
        m = self.model
        if m is None:
            return None
        X_vec = self.pipeline.transform([engineered_feature_dict])
        score = float(m.predict(X_vec)[0])
        return max(0.0, min(100.0, score))
