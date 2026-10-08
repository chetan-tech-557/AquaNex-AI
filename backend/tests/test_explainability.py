"""Tests for Explainable AI (SHAP) feature attributions."""

import pytest
from backend.app.explainability.shap_explainer import ShapExplainerService
from backend.app.data.feature_engineering import engineer_features_from_input


def test_shap_explanation_structure(normal_pond_input):
    explainer = ShapExplainerService()
    features = engineer_features_from_input(normal_pond_input)

    res = explainer.explain_prediction(features, predicted_feed_kg=5.5)

    assert len(res.top_features) > 0
    top = res.top_features[0]
    assert hasattr(top, "feature")
    assert hasattr(top, "display_name")
    assert hasattr(top, "shap_value")
    assert top.impact_direction in ["INCREASES FEED", "DECREASES FEED"]
    assert "Model factor" in res.summary or "predominantly shaped" in res.summary
    assert len(res.bullet_points) > 0
