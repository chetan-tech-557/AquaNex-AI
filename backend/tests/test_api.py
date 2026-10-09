"""Unit and integration tests for AquaNex AI FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient

from backend.app.server import app

client = TestClient(app)


def test_health_check_endpoint():
    """Verify health check returns service and model statuses."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["models_loaded"] is True
    assert "feed_model" in data


def test_root_endpoint():
    """Verify root documentation info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "AquaNex AI Backend" in data["service"]


def test_recommendation_endpoint_flat_frontend_payload():
    """Verify endpoint accepts Next.js frontend flat JSON payload and returns adapted frontend result."""
    payload = {
        "species": "tilapia",
        "stage": "juvenile",
        "stockCount": 10000,
        "avgWeight": 45.0,
        "survival": 92.0,
        "temperature": 27.5,
        "oxygen": 6.2,
        "ammonia": 0.02,
        "ph": 7.4,
        "pondVolume": 800.0,
        "season": "summer",
    }
    response = client.post("/api/v1/recommendation", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Canonical backend schema assertions
    assert "feed_prediction" in data
    assert "waste_prediction" in data
    assert "pollution_risk" in data
    assert "optimization" in data
    assert "explanation" in data
    assert data["feed_prediction"]["recommended_daily_feed_kg"] > 0
    assert len(data["optimization"]["meal_schedule"]) > 0

    # Adapted Next.js frontend feeding result assertions
    assert "frontend_feeding_result" in data
    fe = data["frontend_feeding_result"]
    assert fe is not None
    assert "biomassKg" in fe
    assert "optimizedFeedKg" in fe
    assert "savedKg" in fe
    assert "tempFactor" in fe
    assert "oxygenFactor" in fe
    assert "ammoniaFactor" in fe
    assert "phFactor" in fe
    assert "meals" in fe
    assert len(fe["meals"]) > 0
    assert "projection" in fe
    assert len(fe["projection"]) == 7
    assert "alerts" in fe
    assert fe["suspended"] is False


def test_recommendation_endpoint_validation_error():
    """Verify invalid parameters trigger 422 Unprocessable Entity."""
    invalid_payload = {
        "species": "unknown_fish",
        "stockCount": -50,
        "avgWeight": 0,
        "survival": 150,
        "temperature": 99.0,
        "oxygen": -2.0,
    }
    response = client.post("/api/v1/recommendation", json=invalid_payload)
    assert response.status_code == 422
    assert "detail" in response.json()


def test_ponds_and_history_endpoints():
    """Verify ponds and history retrieval."""
    ponds_res = client.get("/api/v1/ponds")
    assert ponds_res.status_code == 200
    ponds_data = ponds_res.json()
    assert "ponds" in ponds_data
    assert ponds_data["count"] >= 1

    history_res = client.get("/api/v1/history/pond_01")
    assert history_res.status_code == 200
    hist_data = history_res.json()
    assert "history" in hist_data
    assert hist_data["pond_id"] == "pond_01"


def test_recommendation_endpoint_boundary_slider_ranges():
    """Verify endpoint gracefully handles wide UI slider ranges without crashing with 422."""
    boundary_payload = {
        "species": "tilapia",
        "stage": "juvenile",
        "stockCount": 5000,
        "avgWeight": 35.0,
        "survival": 90.0,
        "temperature": 2.0,   # Cold winter water
        "oxygen": 4.5,
        "ammonia": 2.5,       # High TAN from slider
        "ph": 4.2,           # Acidic pH
        "pondVolume": 600.0,
        "season": "winter",
    }
    response = client.post("/api/v1/recommendation", json=boundary_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["feed_prediction"]["recommended_daily_feed_kg"] > 0
    assert data["pollution_risk"]["risk_score"] > 0


def test_shap_feature_values_non_zero():
    """Verify that SHAP explanation cards display actual input values rather than falling back to 0.0."""
    payload = {
        "species": "tilapia",
        "stage": "juvenile",
        "stockCount": 10000,
        "avgWeight": 45.0,
        "survival": 92.0,
        "temperature": 26.0,
        "oxygen": 6.0,
        "ammonia": 0.3,
        "ph": 7.4,
        "pondVolume": 800.0,
        "season": "summer",
    }
    response = client.post("/api/v1/recommendation", json=payload)
    assert response.status_code == 200
    top_feats = response.json()["explanation"]["top_features"]
    assert len(top_feats) > 0

    # Ensure biomass or feed feature value is extracted and non-zero
    numerical_feats = [f for f in top_feats if "Biomass" in f["display_name"] or "Feed" in f["display_name"]]
    for f in numerical_feats:
        assert float(f["value"]) > 0.0, f"Expected non-zero value for {f['display_name']}, got {f['value']}"


def test_presets_risk_differentiation():
    """Verify that ideal conditions produce low pollution risk while hypoxia produces high risk."""
    ideal_payload = {
        "species": "tilapia",
        "stage": "juvenile",
        "stockCount": 10000,
        "avgWeight": 45,
        "survival": 92,
        "temperature": 28,
        "oxygen": 6.5,
        "ammonia": 0.3,
        "ph": 7.5,
        "season": "spring",
    }
    hypoxia_payload = {
        "species": "tilapia",
        "stage": "juvenile",
        "stockCount": 10000,
        "avgWeight": 45,
        "survival": 92,
        "temperature": 31,
        "oxygen": 2.2,
        "ammonia": 1.4,
        "ph": 8.8,
        "season": "summer",
    }
    res_ideal = client.post("/api/v1/recommendation", json=ideal_payload).json()
    res_hypoxia = client.post("/api/v1/recommendation", json=hypoxia_payload).json()

    assert res_ideal["pollution_risk"]["risk_level"] == "LOW"
    assert res_hypoxia["pollution_risk"]["risk_level"] == "HIGH"
    assert res_hypoxia["feed_prediction"]["recommended_daily_feed_kg"] < res_ideal["feed_prediction"]["recommended_daily_feed_kg"]
    assert res_hypoxia["feed_prediction"]["applied_cap"] is not None

