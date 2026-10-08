"""Main entry point for AquaNex AI backend application."""

import sys
import json
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.config.settings import settings
from backend.app.database.db import init_db
from backend.app.services.recommendation_service import get_recommendation
from backend.app.schemas.input_schema import FeedingPredictionInput

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("AquaNexMain")


def main():
    logger.info("Initializing AquaNex AI backend environment...")
    logger.info("Database URL: %s", settings.database_url)
    init_db()

    logger.info("Running baseline verification scenario (Normal Pond)...")
    sample_input = {
        "pond_id": "pond_01",
        "fishSpecies": "Tilapia",
        "growthStage": "Grow-out",
        "fishAgeDays": 190,
        "biomassKg": 250.0,
        "averageFishWeightG": 150.0,
        "temperatureC": 27.0,
        "dissolvedOxygenMgL": 6.2,
        "pH": 7.4,
        "ammoniaMgL": 0.025,
        "nitrateMgL": 22.0,
        "turbidityNtu": 14.0,
        "salinityPpt": 0.5,
        "previousFeedKg": 5.0,
        "recentAverageFeedKg": 5.2,
        "feedingFrequency": 2,
        "feedQualityScore": 82.0,
        "rainfallMm": 8.0,
        "humidityPercent": 66.0,
        "airTemperatureC": 25.5,
    }

    rec = get_recommendation(sample_input, persist=True)

    print("\n" + "=" * 60)
    print(" AQUANEX AI — RECOMMENDATION PIPELINE RESULT")
    print("=" * 60)
    print(f"Pond ID:                {rec.pond_id}")
    print(f"Feed Prediction:        {rec.feed_prediction.recommended_daily_feed_kg:.2f} kg/day ({rec.feed_prediction.model_name})")
    print(f"Optimized Feed:         {rec.optimization.optimized_daily_feed_kg:.2f} kg/day ({rec.optimization.number_of_meals} meals)")
    print(f"Estimated Waste:        {rec.waste_prediction.expected_waste_kg:.2f} kg ({rec.waste_prediction.risk_level} risk, score {rec.waste_prediction.risk_score})")
    print(f"Pollution Risk:         {rec.pollution_risk.risk_level} (score {rec.pollution_risk.risk_score})")
    print(f"Meal Schedule:          {[f'{m.time}: {m.quantity_kg}kg' for m in rec.optimization.meal_schedule]}")
    if rec.optimization.baseline_comparison:
        b = rec.optimization.baseline_comparison
        print(f"Static Chart Baseline:  {b.baseline_feed_kg:.2f} kg/day (${b.baseline_daily_cost:.2f})")
        print(f"Feed Saved:             {b.feed_saved_kg:.2f} kg/day | Cost Saved: ${b.cost_saved_usd:.2f}/day")
    print("\nTop Contributing Factors (SHAP/Ensemble):")
    for feat in rec.explanation.top_features[:4]:
        print(f" - {feat.display_name}: {feat.value} (Impact: {feat.impact_direction}, SHAP: {feat.shap_value:+.2f})")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
