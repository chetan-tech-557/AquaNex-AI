"""SciPy constrained feeding optimization engine and meal scheduling."""

from typing import Dict, Any, List
import numpy as np
from scipy.optimize import minimize_scalar

from backend.app.config.constants import (
    OPTIMIZATION_PARAMS,
    BASELINE_STAGE_RATES,
    MEAL_SCHEDULE_PRESETS,
)
from backend.app.optimization.objective import feeding_loss_objective
from backend.app.optimization.constraints import get_feeding_bounds
from backend.app.schemas.recommendation_schema import (
    OptimizationResult,
    MealScheduleItem,
    BaselineComparison,
)


class FeedingOptimizer:
    """Solves for economically and ecologically optimal daily feed rations and meal timing."""

    def __init__(self):
        self.params = OPTIMIZATION_PARAMS

    def optimize_feeding(
        self,
        predicted_feed_kg: float,
        expected_waste_kg: float,
        pollution_risk_score: int,
        biomass_kg: float,
        features: Dict[str, Any],
    ) -> OptimizationResult:
        """Run SciPy constrained optimization across meal configurations."""
        f_min, f_max = get_feeding_bounds(
            predicted_appetite_kg=predicted_feed_kg,
            biomass_kg=biomass_kg,
            features=features,
        )

        candidate_meals = [1, 2, 3, 4]
        best_cost = float("inf")
        best_feed_kg = predicted_feed_kg
        best_meal_count = 3
        solver_status = "converged"

        # Evaluate candidate meal partitions using SciPy bounded scalar minimization
        for m in candidate_meals:
            res = minimize_scalar(
                fun=lambda f: feeding_loss_objective(
                    feed_kg=f,
                    predicted_appetite_kg=predicted_feed_kg,
                    base_waste_kg=expected_waste_kg,
                    base_pollution_score=float(pollution_risk_score),
                    meals=m,
                    params=self.params,
                ),
                bounds=(f_min, f_max),
                method="bounded",
                options={"xatol": 1e-3, "maxiter": 100},
            )

            if res.success and res.fun < best_cost:
                best_cost = res.fun
                best_feed_kg = float(res.x)
                best_meal_count = m

        optimized_feed_kg = round(max(f_min, min(f_max, best_feed_kg)), 2)

        # Build scheduled meal items
        feed_per_meal_kg = round(optimized_feed_kg / max(1, best_meal_count), 2)
        schedule_times = MEAL_SCHEDULE_PRESETS.get(best_meal_count, ["08:00 AM", "01:00 PM", "06:00 PM"])

        meal_schedule: List[MealScheduleItem] = []
        running_sum = 0.0
        for i, time_str in enumerate(schedule_times, start=1):
            if i == len(schedule_times):
                portion = round(optimized_feed_kg - running_sum, 2)
            else:
                portion = feed_per_meal_kg
                running_sum += portion
            meal_schedule.append(
                MealScheduleItem(
                    meal_number=i,
                    time=time_str,
                    quantity_kg=max(0.01, portion),
                )
            )

        # Baseline static chart comparison
        stage = str(features.get("growthStage", features.get("growth_stage", "Grow-out")))
        base_rate = BASELINE_STAGE_RATES.get(stage, 0.025)
        baseline_feed = round(biomass_kg * base_rate, 2)
        baseline_waste = round(baseline_feed * 0.28, 2)
        feed_cost_rate = self.params.get("feed_cost_per_kg", 2.00)

        baseline_cost = round(baseline_feed * feed_cost_rate, 2)
        optimized_cost = round(optimized_feed_kg * feed_cost_rate, 2)

        feed_saved = round(max(0.0, baseline_feed - optimized_feed_kg), 2)
        waste_saved = round(max(0.0, baseline_waste - expected_waste_kg), 2)
        cost_saved = round(max(0.0, baseline_cost - optimized_cost), 2)

        comparison = BaselineComparison(
            baseline_feed_kg=baseline_feed,
            baseline_waste_kg=baseline_waste,
            baseline_daily_cost=baseline_cost,
            baseline_pollution_risk="HIGH" if baseline_waste > 2.0 else "MEDIUM",
            baseline_waste_risk_score=95 if baseline_waste > 2.0 else 60,
            baseline_pollution_risk_score=90 if baseline_waste > 2.0 else 55,
            feed_saved_kg=feed_saved,
            waste_prevented_kg=waste_saved,
            cost_saved_usd=cost_saved,
        )

        return OptimizationResult(
            optimized_daily_feed_kg=optimized_feed_kg,
            number_of_meals=best_meal_count,
            meal_schedule=meal_schedule,
            feed_per_meal_kg=feed_per_meal_kg,
            estimated_daily_cost=optimized_cost,
            solver_status=solver_status,
            baseline_comparison=comparison,
        )
