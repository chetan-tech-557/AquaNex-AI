"""Tests for SciPy constrained optimization and meal scheduling."""

import pytest
from backend.app.optimization.optimizer import FeedingOptimizer
from backend.app.data.feature_engineering import engineer_features_from_input


def test_optimization_execution(normal_pond_input):
    optimizer = FeedingOptimizer()
    features = engineer_features_from_input(normal_pond_input)

    res = optimizer.optimize_feeding(
        predicted_feed_kg=5.5,
        expected_waste_kg=0.4,
        pollution_risk_score=20,
        biomass_kg=250.0,
        features=features,
    )

    assert res.optimized_daily_feed_kg > 0.0
    assert res.number_of_meals in [1, 2, 3, 4]
    assert len(res.meal_schedule) == res.number_of_meals

    # Check that individual meal quantities sum to total daily feed (within rounding error)
    total_meal_sum = sum(m.quantity_kg for m in res.meal_schedule)
    assert pytest.approx(total_meal_sum, 0.05) == res.optimized_daily_feed_kg

    # Check baseline comparison
    assert res.baseline_comparison is not None
    assert res.baseline_comparison.baseline_feed_kg > 0.0
    assert res.baseline_comparison.baseline_daily_cost > 0.0
