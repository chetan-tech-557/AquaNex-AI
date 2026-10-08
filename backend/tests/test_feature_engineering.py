"""Tests for feature engineering and transformation pipeline."""

import pytest
from backend.app.data.feature_engineering import engineer_features_from_input, engineer_features_dict
from backend.app.data.preprocessing import AquaNexPreprocessor


def test_feature_engineering_calculations(normal_pond_input):
    features = engineer_features_from_input(normal_pond_input)

    assert "feed_to_biomass_ratio" in features
    # 5.0 kg / 250.0 kg = 0.02
    assert pytest.approx(features["feed_to_biomass_ratio"], 0.001) == 0.02

    assert "temperature_deviation" in features
    # Tilapia optimal is 28.0. Temp is 27.0 -> deviation is 1.0
    assert pytest.approx(features["temperature_deviation"], 0.001) == 1.0

    assert "recent_feeding_trend" in features
    # 5.0 - 5.2 = -0.2
    assert pytest.approx(features["recent_feeding_trend"], 0.001) == -0.2

    assert features["fish_count"] > 0
    assert features["biomass_per_fish"] > 0


def test_preprocessor_shape_and_names(normal_pond_input):
    features = engineer_features_from_input(normal_pond_input)
    preprocessor = AquaNexPreprocessor()
    preprocessor.fit([features])

    vec = preprocessor.transform([features])
    names = preprocessor.get_feature_names_out()

    assert vec.shape == (1, len(names))
    assert "species_Tilapia" in names
    assert "species_Salmon" in names
    assert "stage_Adult" in names
