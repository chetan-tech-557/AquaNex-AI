"""Feed model wrapper encapsulating inference and pipeline application."""

from typing import Dict, Any, List
import numpy as np
from backend.app.models.model_loader import get_feed_model, get_feed_pipeline


class FeedModelWrapper:
    """Wrapper around trained feed requirement regressor."""

    def __init__(self):
        self._model = None
        self._pipeline = None

    @property
    def model(self):
        if self._model is None:
            self._model = get_feed_model()
        return self._model

    @property
    def pipeline(self):
        if self._pipeline is None:
            self._pipeline = get_feed_pipeline()
        return self._pipeline

    def predict(self, engineered_feature_dict: Dict[str, Any]) -> float:
        """Run inference on a single engineered feature dictionary."""
        X_vec = self.pipeline.transform([engineered_feature_dict])
        pred = float(self.model.predict(X_vec)[0])
        return max(0.0, pred)

    def get_feature_names(self) -> List[str]:
        """Return list of encoded feature names."""
        return self.pipeline.get_feature_names_out()
