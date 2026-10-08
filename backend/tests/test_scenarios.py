"""Integration test suite executing the 6 required Hackathon demo scenarios."""

import pytest
from backend.app.services.recommendation_service import get_recommendation


def test_scenario_1_normal_pond(normal_pond_input):
    """Scenario 1: Normal healthy pond conditions."""
    rec = get_recommendation(normal_pond_input, persist=False)

    assert rec.feed_prediction.recommended_daily_feed_kg > 0.0
    assert rec.optimization.optimized_daily_feed_kg > 0.0
    assert rec.waste_prediction.risk_level in ["LOW", "MEDIUM"]
    assert rec.pollution_risk.risk_level in ["LOW", "MEDIUM"]
    assert len(rec.optimization.meal_schedule) >= 1
    assert len(rec.explanation.top_features) >= 3


def test_scenario_2_low_do(normal_pond_input, low_do_input):
    """Scenario 2: Low dissolved oxygen (hypoxia)."""
    normal_rec = get_recommendation(normal_pond_input, persist=False)
    low_do_rec = get_recommendation(low_do_input, persist=False)

    # Hypoxia should curtail feed recommendation and elevate risk
    assert low_do_rec.feed_prediction.recommended_daily_feed_kg < normal_rec.feed_prediction.recommended_daily_feed_kg
    assert low_do_rec.pollution_risk.risk_score > normal_rec.pollution_risk.risk_score
    assert any("oxygen" in f.lower() or "hypoxia" in f.lower() for f in low_do_rec.pollution_risk.contributing_factors + low_do_rec.warnings)


def test_scenario_3_high_ammonia(normal_pond_input, high_ammonia_input):
    """Scenario 3: Elevated toxic ammonia."""
    normal_rec = get_recommendation(normal_pond_input, persist=False)
    high_amm_rec = get_recommendation(high_ammonia_input, persist=False)

    assert high_amm_rec.pollution_risk.risk_score > normal_rec.pollution_risk.risk_score
    assert high_amm_rec.pollution_risk.risk_level in ["MEDIUM", "HIGH"]
    assert any("ammonia" in f.lower() for f in high_amm_rec.pollution_risk.contributing_factors)


def test_scenario_4_high_turbidity(normal_pond_input, high_turbidity_input):
    """Scenario 4: High turbidity (suspended sediment)."""
    normal_rec = get_recommendation(normal_pond_input, persist=False)
    turb_rec = get_recommendation(high_turbidity_input, persist=False)

    assert turb_rec.pollution_risk.risk_score > normal_rec.pollution_risk.risk_score
    assert any("turbidity" in f.lower() for f in turb_rec.pollution_risk.contributing_factors)


def test_scenario_5_different_fish_age(normal_pond_input, different_fish_age_input):
    """Scenario 5: Different fish age (mature adult vs grow-out)."""
    growout_rec = get_recommendation(normal_pond_input, persist=False)
    adult_rec = get_recommendation(different_fish_age_input, persist=False)

    # The models respond to biological age and stage differences
    assert adult_rec.feed_prediction.recommended_daily_feed_kg != growout_rec.feed_prediction.recommended_daily_feed_kg
    assert adult_rec.optimization.optimized_daily_feed_kg > 0.0


def test_scenario_6_different_biomass(normal_pond_input, different_biomass_input):
    """Scenario 6: Different biomass (850 kg vs 250 kg)."""
    low_biomass_rec = get_recommendation(normal_pond_input, persist=False)
    high_biomass_rec = get_recommendation(different_biomass_input, persist=False)

    # Higher biomass naturally requires higher total daily feed
    assert high_biomass_rec.feed_prediction.recommended_daily_feed_kg > low_biomass_rec.feed_prediction.recommended_daily_feed_kg
    assert high_biomass_rec.optimization.optimized_daily_feed_kg > low_biomass_rec.optimization.optimized_daily_feed_kg
