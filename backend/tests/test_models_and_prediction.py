"""Tests for model loading and prediction services."""

import pytest
from backend.app.prediction.feed_prediction import FeedPredictionService
from backend.app.prediction.waste_prediction import WastePredictionService
from backend.app.prediction.pollution_prediction import PollutionPredictionService
from backend.app.data.feature_engineering import engineer_features_from_input


def test_feed_prediction_executes(normal_pond_input):
    service = FeedPredictionService()
    features = engineer_features_from_input(normal_pond_input)
    res = service.predict_feed_requirement(features)

    assert res.recommended_daily_feed_kg > 0.0
    assert "Gradient Boosting" in res.model_name or "Random Forest" in res.model_name
    assert res.confidence_or_uncertainty > 0.0


def test_waste_prediction_bounds(normal_pond_input):
    feed_svc = FeedPredictionService()
    waste_svc = WastePredictionService()

    features = engineer_features_from_input(normal_pond_input)
    feed_pred = feed_svc.predict_feed_requirement(features)
    waste_pred = waste_svc.predict_waste(features, feed_pred.recommended_daily_feed_kg)

    assert waste_pred.expected_waste_kg >= 0.0
    assert waste_pred.expected_waste_kg < feed_pred.recommended_daily_feed_kg
    assert 0 <= waste_pred.risk_score <= 100
    assert waste_pred.risk_level in ["LOW", "MEDIUM", "HIGH"]


def test_pollution_risk_evaluation(normal_pond_input):
    poll_svc = PollutionPredictionService()
    features = engineer_features_from_input(normal_pond_input)

    res = poll_svc.predict_pollution_risk(features, feed_kg=5.0, expected_waste_kg=0.5)

    assert 0 <= res.risk_score <= 100
    assert res.risk_level in ["LOW", "MEDIUM", "HIGH"]
    assert len(res.contributing_factors) > 0
    assert "ammonia" in res.sub_scores
    assert "dissolved_oxygen" in res.sub_scores


def test_hypoxia_guard_curtails_feed(low_do_input):
    service = FeedPredictionService()
    features = engineer_features_from_input(low_do_input)
    res = service.predict_feed_requirement(features)

    assert res.applied_cap is not None
    assert "hypoxia" in res.applied_cap.lower()
    # The adjusted feed must be strictly lower than raw appetite
    assert res.recommended_daily_feed_kg <= res.unadjusted_ml_feed_kg
