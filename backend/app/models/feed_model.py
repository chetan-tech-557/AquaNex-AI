"""Feed model wrapper encapsulating inference and pipeline application."""

from typing import Dict, Any, List
import numpy as np
import pandas as pd
from backend.app.models.model_loader import get_feed_model, get_feed_pipeline


def normalize_feed_features(r: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure all required tabular numerical and categorical features exist with biological defaults."""
    biomass = float(r.get("biomass_kg", r.get("biomassKg", 250.0)))
    avg_weight = float(r.get("avg_weight_g", r.get("averageFishWeightG", 45.0)))
    count = r.get("fish_count") or r.get("fishCount")
    if not count or float(count) <= 0:
        count = max(1, int(round((biomass * 1000.0) / max(0.1, avg_weight))))
    else:
        count = int(count)

    prev_feed_g = r.get("previous_feed_g")
    if prev_feed_g is None:
        prev_feed_kg = float(r.get("previousFeedKg", r.get("previous_feed_kg", 5.0)))
        prev_feed_g = prev_feed_kg * 1000.0

    return {
        "biomass_kg": biomass,
        "fish_count": count,
        "avg_weight_g": avg_weight,
        "water_temperature_c": float(r.get("water_temperature_c", r.get("temperatureC", 27.0))),
        "dissolved_oxygen_mg_l": float(r.get("dissolved_oxygen_mg_l", r.get("dissolvedOxygenMgL", 6.2))),
        "ph": float(r.get("ph", r.get("pH", 7.4))),
        "turbidity_ntu": float(r.get("turbidity_ntu", r.get("turbidityNtu", 12.0))),
        "ammonia_mg_l": float(r.get("ammonia_mg_l", r.get("ammoniaMgL", 0.02))),
        "nitrate_mg_l": float(r.get("nitrate_mg_l", r.get("nitrateMgL", 2.5))),
        "previous_feed_g": float(prev_feed_g),
        "air_temperature_c": float(r.get("air_temperature_c", r.get("airTemperatureC", 26.0))),
        "rainfall_mm": float(r.get("rainfall_mm", r.get("rainfallMm", 10.0))),
        "relative_humidity_pct": float(r.get("relative_humidity_pct", r.get("humidityPercent", 65.0))),
        "species": str(r.get("species", r.get("fishSpecies", "Tilapia"))).capitalize(),
        "growth_stage": str(r.get("growth_stage", r.get("growthStage", "Juvenile"))).capitalize(),
        "season": str(r.get("season", "Summer")).capitalize(),
    }


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
        """Run inference on a single engineered feature dictionary (returns feed in kg/day)."""
        row = normalize_feed_features(engineered_feature_dict)
        df_row = pd.DataFrame([row])
        X_vec = self.pipeline.transform(df_row)
        pred_kg = float(self.model.predict(X_vec)[0])
        return max(0.0, pred_kg)

    def get_feature_names(self) -> List[str]:
        """Return list of encoded feature names."""
        return list(self.pipeline.get_feature_names_out())
