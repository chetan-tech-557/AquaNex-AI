"""Pollution model wrapper encapsulating ML score prediction."""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from backend.app.models.model_loader import get_pollution_model, get_pollution_pipeline


def normalize_pollution_features(r: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure all required features exist for pollution risk score prediction."""
    biomass = float(r.get("biomass_kg", r.get("biomassKg", 250.0)))
    prev_waste_g = r.get("previous_feed_waste_g")
    if prev_waste_g is None:
        prev_feed_kg = float(r.get("previousFeedKg", r.get("previous_feed_kg", 5.0)))
        prev_waste_g = prev_feed_kg * 1000.0 * 0.10  # approximate 10% uneaten

    return {
        "biomass_kg": biomass,
        "water_temperature_c": float(r.get("water_temperature_c", r.get("temperatureC", 27.0))),
        "dissolved_oxygen_mg_l": float(r.get("dissolved_oxygen_mg_l", r.get("dissolvedOxygenMgL", 6.2))),
        "ph": float(r.get("ph", r.get("pH", 7.4))),
        "turbidity_ntu": float(r.get("turbidity_ntu", r.get("turbidityNtu", 12.0))),
        "ammonia_mg_l": float(r.get("ammonia_mg_l", r.get("ammoniaMgL", 0.02))),
        "nitrite_mg_l": float(r.get("nitrite_mg_l", 0.025)),
        "nitrate_mg_l": float(r.get("nitrate_mg_l", r.get("nitrateMgL", 2.5))),
        "rainfall_mm": float(r.get("rainfall_mm", r.get("rainfallMm", 10.0))),
        "relative_humidity_pct": float(r.get("relative_humidity_pct", r.get("humidityPercent", 65.0))),
        "previous_feed_waste_g": float(prev_waste_g),
        "species": str(r.get("species", r.get("fishSpecies", "Tilapia"))).capitalize(),
        "growth_stage": str(r.get("growth_stage", r.get("growthStage", "Juvenile"))).capitalize(),
        "season": str(r.get("season", "Summer")).capitalize(),
    }


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
            self._pipeline = get_pollution_pipeline()
        return self._pipeline

    def predict_score(self, engineered_feature_dict: Dict[str, Any]) -> Optional[float]:
        """Predict continuous pollution risk score (0-100) if model is available."""
        m = self.model
        p = self.pipeline
        if m is None or p is None:
            return None
        row = normalize_pollution_features(engineered_feature_dict)
        df_row = pd.DataFrame([row])
        X_vec = p.transform(df_row)
        score = float(m.predict(X_vec)[0])
        return max(0.0, min(100.0, score))
