"""Objective function formulation for SciPy feeding optimization.

Minimizes aggregate aquaculture loss: direct feed cost + unconsumed waste penalty + pollution penalty.
"""

from typing import Dict, Any
from backend.app.config.constants import OPTIMIZATION_PARAMS


def feeding_loss_objective(
    feed_kg: float,
    predicted_appetite_kg: float,
    base_waste_kg: float,
    base_pollution_score: float,
    meals: int,
    params: Dict[str, float] = None,
) -> float:
    """Calculate aggregate penalty for a given feed quantity and meal count.

    Terms:
    1. Direct feed purchase cost: C_feed * feed_kg
    2. Water fouling waste cost: C_waste * uneaten_feed(feed_kg, meals)
    3. Pond ecological pollution penalty: lambda_poll * pollution_score(feed_kg)
    4. Meal operational complexity cost: mu_meal * (meals - 1)
    """
    if params is None:
        params = OPTIMIZATION_PARAMS

    feed_cost_per_kg = params.get("feed_cost_per_kg", 2.00)
    waste_penalty_per_kg = params.get("waste_penalty_per_kg", 12.00)
    pollution_weight = params.get("pollution_penalty_weight", 0.15)
    meal_penalty = params.get("meal_complexity_penalty", 0.10)

    # 1. Direct feed cost
    cost_feed = feed_cost_per_kg * feed_kg

    # 2. Expected waste calculation:
    # Splitting into more meals reduces per-meal bolus waste by factor (1 / sqrt(meals)).
    # Exceeding predicted appetite causes exponential pellet loss.
    appetite = max(0.5, predicted_appetite_kg)
    feed_ratio = feed_kg / appetite

    if feed_ratio > 1.0:
        waste_scaling = 1.0 + 2.5 * (feed_ratio - 1.0) ** 1.8
    else:
        waste_scaling = feed_ratio ** 1.2

    meal_efficiency = (2.0 / max(1, meals)) ** 0.4
    estimated_waste = base_waste_kg * waste_scaling * meal_efficiency
    cost_waste = waste_penalty_per_kg * estimated_waste

    # 3. Dynamic pollution penalty
    # Higher feeding adds biochemical oxygen demand (BOD)
    pollution_inflation = 1.0 + 0.25 * max(0.0, feed_ratio - 0.9)
    adjusted_pollution = min(100.0, base_pollution_score * pollution_inflation)
    cost_pollution = pollution_weight * adjusted_pollution

    # 4. Operational meal complexity
    cost_operational = meal_penalty * max(0, meals - 1)

    total_loss = cost_feed + cost_waste + cost_pollution + cost_operational
    return total_loss
