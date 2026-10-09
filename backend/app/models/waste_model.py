"""Waste model wrapper encapsulating inference and pipeline application."""

from typing import Dict, Any
import numpy as np
import pandas as pd
from backend.app.models.model_loader import get_waste_model, get_waste_pipeline


def normalize_waste_features(r: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure all required features exist for waste prediction."""
    biomass = float(r.get("biomass_kg", r.get("biomassKg", 250.0)))
    prev_feed_g = r.get("previous_feed_g")
    if prev_feed_g is None:
        prev_feed_kg = float(r.get("previousFeedKg", r.get("previous_feed_kg", 5.0)))
        prev_feed_g = prev_feed_kg * 1000.0

    prev_consumed_g = r.get("previous_feed_consumed_g")
    if prev_consumed_g is None:
        prev_consumed_g = prev_feed_g * 0.90

    prev_waste_g = r.get("previous_feed_waste_g")
    if prev_waste_g is None:
        prev_waste_g = max(0.0, prev_feed_g - prev_consumed_g)

    return {
        "biomass_kg": biomass,
        "water_temperature_c": float(r.get("water_temperature_c", r.get("temperatureC", 27.0))),
        "dissolved_oxygen_mg_l": float(r.get("dissolved_oxygen_mg_l", r.get("dissolvedOxygenMgL", 6.2))),
        "ph": float(r.get("ph", r.get("pH", 7.4))),
        "ammonia_mg_l": float(r.get("ammonia_mg_l", r.get("ammoniaMgL", 0.02))),
        "turbidity_ntu": float(r.get("turbidity_ntu", r.get("turbidityNtu", 12.0))),
        "previous_feed_g": float(prev_feed_g),
        "previous_feed_consumed_g": float(prev_consumed_g),
        "previous_feed_waste_g": float(prev_waste_g),
        "fish_activity_score": float(r.get("fish_activity_score", 0.88)),
        "weather_stress_score": float(r.get("weather_stress_score", 0.05)),
        "species": str(r.get("species", r.get("fishSpecies", "Tilapia"))).capitalize(),
        "growth_stage": str(r.get("growth_stage", r.get("growthStage", "Juvenile"))).capitalize(),
        "season": str(r.get("season", "Summer")).capitalize(),
    }


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
            self._pipeline = get_waste_pipeline()
        return self._pipeline

    def predict_pct(self, engineered_feature_dict: Dict[str, Any]) -> float:
        """Predict expected uneaten feed waste percentage (0.5% - 30.0%)."""
        row = normalize_waste_features(engineered_feature_dict)
        df_row = pd.DataFrame([row])
        X_vec = self.pipeline.transform(df_row)
        pct = float(self.model.predict(X_vec)[0])
        return max(0.5, min(40.0, pct))

    def predict(self, engineered_feature_dict: Dict[str, Any]) -> float:
        """Predict expected uneaten feed in kilograms based on baseline ration."""
        pct = self.predict_pct(engineered_feature_dict)
        prev_feed_kg = float(engineered_feature_dict.get("previousFeedKg", engineered_feature_dict.get("previous_feed_kg", 5.0)))
        expected_waste_kg = prev_feed_kg * (pct / 100.0)
        return max(0.05, round(expected_waste_kg, 2))
