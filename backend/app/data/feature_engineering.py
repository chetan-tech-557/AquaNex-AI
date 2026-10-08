"""Feature engineering pipeline for AquaNex AI.

Transforms validated biological, water chemistry, feeding history, and weather variables
into domain-informed features for ML regression and risk assessment.
"""

from typing import Dict, Any, Union
import numpy as np
import pandas as pd
from backend.app.schemas.input_schema import FeedingPredictionInput
from backend.app.config.constants import SPECIES_PROFILES


def engineer_features_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Engineer derived features from a flat dictionary of inputs."""
    species = str(data.get("fishSpecies", data.get("species", "Tilapia")))
    profile = SPECIES_PROFILES.get(species, SPECIES_PROFILES["Tilapia"])

    biomass_kg = float(data.get("biomassKg", data.get("biomass_kg", 250.0)))
    previous_feed_kg = float(data.get("previousFeedKg", data.get("previous_feed_kg", 5.0)))
    recent_avg_feed_kg = float(data.get("recentAverageFeedKg", data.get("recent_average_feed_kg", 5.2)))
    avg_weight_g = float(data.get("averageFishWeightG", data.get("average_fish_weight_g", 150.0)))
    temp_c = float(data.get("temperatureC", data.get("water_temperature_c", 27.0)))
    do_mg_l = float(data.get("dissolvedOxygenMgL", data.get("dissolved_oxygen_mg_l", 6.2)))
    ammonia_mg_l = float(data.get("ammoniaMgL", data.get("ammonia_mg_l", 0.025)))
    feed_quality = float(data.get("feedQualityScore", data.get("feed_quality_score", 82.0)))

    # Fish count
    fish_count = data.get("fish_count") or data.get("fishCount")
    if fish_count is None or fish_count <= 0:
        fish_count = max(1, int(round((biomass_kg * 1000.0) / max(0.1, avg_weight_g))))
    else:
        fish_count = int(fish_count)

    # 1. Feed-to-biomass ratio (prior day feeding intensity)
    feed_to_biomass_ratio = previous_feed_kg / max(1.0, biomass_kg)

    # 2. Biomass per fish (kg/fish)
    biomass_per_fish = biomass_kg / max(1, fish_count)

    # 3. Temperature deviation from species-specific biological optimum
    optimal_temp = profile["optimal_temperature_c"]
    temperature_deviation = abs(temp_c - optimal_temp)

    # 4. Dissolved oxygen stress indicator (extent DO falls below species requirement)
    target_do = profile["min_do_mg_l"]
    do_stress_indicator = max(0.0, target_do - do_mg_l)

    # 5. Ammonia toxicity stress indicator
    target_ammonia = profile["max_ammonia_mg_l"]
    ammonia_stress_indicator = max(0.0, ammonia_mg_l - target_ammonia)

    # 6. Recent feeding trend (surge or drop compared to rolling history)
    recent_feeding_trend = previous_feed_kg - recent_avg_feed_kg

    # 7. Feed quality normalized factor
    feed_quality_factor = np.clip(feed_quality / 100.0, 0.0, 1.0)

    # Combine all raw + engineered features
    out = dict(data)
    out["feed_to_biomass_ratio"] = float(feed_to_biomass_ratio)
    out["biomass_per_fish"] = float(biomass_per_fish)
    out["temperature_deviation"] = float(temperature_deviation)
    out["do_stress_indicator"] = float(do_stress_indicator)
    out["ammonia_stress_indicator"] = float(ammonia_stress_indicator)
    out["recent_feeding_trend"] = float(recent_feeding_trend)
    out["feed_quality_factor"] = float(feed_quality_factor)
    out["fish_count"] = int(fish_count)
    return out


def engineer_features_from_input(user_input: FeedingPredictionInput) -> Dict[str, Any]:
    """Convert strongly-typed FeedingPredictionInput into engineered dictionary."""
    raw_dict = {
        "fishSpecies": user_input.fish.species,
        "growthStage": user_input.fish.growth_stage,
        "fishAgeDays": user_input.fish.fish_age_days,
        "biomassKg": user_input.fish.biomass_kg,
        "averageFishWeightG": user_input.fish.average_fish_weight_g,
        "fish_count": user_input.fish.fish_count,
        "temperatureC": user_input.water.water_temperature_c,
        "dissolvedOxygenMgL": user_input.water.dissolved_oxygen_mg_l,
        "pH": user_input.water.ph,
        "ammoniaMgL": user_input.water.ammonia_mg_l,
        "nitrateMgL": user_input.water.nitrate_mg_l,
        "turbidityNtu": user_input.water.turbidity,
        "salinityPpt": user_input.water.salinity_ppt,
        "previousFeedKg": user_input.feeding.previous_feed_kg,
        "recentAverageFeedKg": user_input.feeding.recent_average_feed_kg,
        "feedingFrequency": user_input.feeding.feeding_frequency,
        "feedQualityScore": user_input.feeding.feed_quality_score,
        "rainfallMm": user_input.environment.rainfall_mm,
        "humidityPercent": user_input.environment.humidity_percent,
        "airTemperatureC": user_input.environment.air_temperature_c,
    }
    return engineer_features_dict(raw_dict)


def engineer_features_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Apply feature engineering across an entire pandas DataFrame."""
    records = df.to_dict(orient="records")
    engineered = [engineer_features_dict(r) for r in records]
    return pd.DataFrame(engineered)
