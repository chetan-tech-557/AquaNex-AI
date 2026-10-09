"""Tests for trained ML models, metadata, and generalization performance."""

import json
from pathlib import Path
import pytest
import joblib

from backend.app.config.settings import settings
from backend.app.models.feed_model import FeedModelWrapper
from backend.app.models.waste_model import WasteModelWrapper
from backend.app.models.pollution_model import PollutionModelWrapper


def test_model_files_and_metadata_exist():
    """Verify that all three trained models and their JSON metadata exist on disk."""
    assert settings.feed_model_path.exists(), "feed_model.joblib missing"
    assert settings.waste_model_path.exists(), "waste_model.joblib missing"
    assert settings.pollution_model_path.exists(), "pollution_model.joblib missing"

    feed_meta_path = settings.trained_models_dir / "feed_model_metadata.json"
    waste_meta_path = settings.trained_models_dir / "waste_model_metadata.json"
    pollution_meta_path = settings.trained_models_dir / "pollution_model_metadata.json"

    assert feed_meta_path.exists()
    assert waste_meta_path.exists()
    assert pollution_meta_path.exists()

    with open(feed_meta_path) as f:
        feed_meta = json.load(f)
    assert feed_meta["metrics"]["test_r2"] > 0.95
    assert feed_meta["training_rows"] > 100000

    with open(waste_meta_path) as f:
        waste_meta = json.load(f)
    assert waste_meta["metrics"]["test_r2"] > 0.90

    with open(pollution_meta_path) as f:
        poll_meta = json.load(f)
    assert poll_meta["metrics"]["test_r2"] > 0.90


def test_feed_model_inference():
    """Verify FeedModelWrapper predicts reasonable non-negative feed requirement."""
    wrapper = FeedModelWrapper()
    features = {
        "biomass_kg": 500.0,
        "fish_count": 10000,
        "avg_weight_g": 50.0,
        "water_temperature_c": 28.0,
        "dissolved_oxygen_mg_l": 6.5,
        "ph": 7.5,
        "ammonia_mg_l": 0.02,
        "turbidity_ntu": 12.0,
        "nitrate_mg_l": 2.5,
        "previous_feed_g": 20000.0,
        "species": "Tilapia",
        "growth_stage": "Juvenile",
        "season": "Summer",
    }
    feed_kg = wrapper.predict(features)
    assert isinstance(feed_kg, float)
    assert feed_kg > 0.0
    # For 500 kg biomass juvenile tilapia, feed should be between 5 kg and 35 kg
    assert 5.0 <= feed_kg <= 35.0


def test_waste_model_inference():
    """Verify WasteModelWrapper predicts bounded uneaten feed percentage."""
    wrapper = WasteModelWrapper()
    features = {
        "biomass_kg": 500.0,
        "water_temperature_c": 28.0,
        "dissolved_oxygen_mg_l": 6.5,
        "ph": 7.5,
        "ammonia_mg_l": 0.02,
        "turbidity_ntu": 12.0,
        "previous_feed_g": 20000.0,
        "species": "Tilapia",
        "growth_stage": "Juvenile",
        "season": "Summer",
    }
    pct = wrapper.predict_pct(features)
    assert isinstance(pct, float)
    assert 0.5 <= pct <= 35.0


def test_pollution_model_inference():
    """Verify PollutionModelWrapper predicts bounded 0-100 risk score."""
    wrapper = PollutionModelWrapper()
    features = {
        "biomass_kg": 500.0,
        "water_temperature_c": 28.0,
        "dissolved_oxygen_mg_l": 6.5,
        "ph": 7.5,
        "ammonia_mg_l": 0.02,
        "turbidity_ntu": 12.0,
        "nitrite_mg_l": 0.025,
        "nitrate_mg_l": 2.5,
        "rainfall_mm": 5.0,
        "relative_humidity_pct": 60.0,
        "previous_feed_waste_g": 1500.0,
        "species": "Tilapia",
        "growth_stage": "Juvenile",
        "season": "Summer",
    }
    score = wrapper.predict_score(features)
    assert isinstance(score, float)
    assert 0.0 <= score <= 100.0
