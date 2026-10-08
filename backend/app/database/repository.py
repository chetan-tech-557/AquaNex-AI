"""Data access repository for AquaNex AI SQLite storage."""

import json
import logging
from typing import List, Dict, Any, Optional
from backend.app.database.db import get_db_connection, init_db
from backend.app.schemas.recommendation_schema import FinalRecommendationResponse
from backend.app.schemas.input_schema import FeedingPredictionInput

logger = logging.getLogger("Repository")


class AquacultureRepository:
    """Repository handling persistence of pond status, metrics, and recommendations."""

    def __init__(self):
        init_db()

    def create_or_get_pond(self, pond_id: str, name: Optional[str] = None) -> Dict[str, Any]:
        """Ensure pond exists in database, creating if necessary."""
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM ponds WHERE pond_id = ?", (pond_id,))
            row = cur.fetchone()
            if row:
                return dict(row)

            pond_name = name or f"Pond {pond_id}"
            cur.execute(
                "INSERT INTO ponds (pond_id, name, volume_m3, location) VALUES (?, ?, ?, ?)",
                (pond_id, pond_name, 500.0, "AquaNex Demonstration Farm"),
            )
            cur.execute("SELECT * FROM ponds WHERE pond_id = ?", (pond_id,))
            return dict(cur.fetchone())

    def list_ponds(self) -> List[Dict[str, Any]]:
        """List all ponds registered in the system."""
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM ponds ORDER BY created_at ASC")
            return [dict(r) for r in cur.fetchall()]

    def save_recommendation(
        self,
        user_input: FeedingPredictionInput,
        rec: FinalRecommendationResponse,
    ) -> int:
        """Persist recommendation, water readings, and feeding state to SQLite."""
        pond_id = user_input.pond_id or "pond_01"
        self.create_or_get_pond(pond_id)

        schedule_json = json.dumps([item.model_dump() for item in rec.optimization.meal_schedule])

        with get_db_connection() as conn:
            cur = conn.cursor()

            # 1. Log water quality
            cur.execute(
                """
                INSERT INTO water_measurements (
                    pond_id, water_temperature_c, dissolved_oxygen_mg_l, ph,
                    ammonia_mg_l, nitrate_mg_l, turbidity, salinity_ppt
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pond_id,
                    user_input.water.water_temperature_c,
                    user_input.water.dissolved_oxygen_mg_l,
                    user_input.water.ph,
                    user_input.water.ammonia_mg_l,
                    user_input.water.nitrate_mg_l,
                    user_input.water.turbidity,
                    user_input.water.salinity_ppt,
                ),
            )

            # 2. Log fish stock
            cur.execute(
                """
                INSERT INTO fish_stocks (
                    pond_id, species, growth_stage, fish_age_days,
                    fish_count, biomass_kg, average_fish_weight_g
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pond_id,
                    user_input.fish.species,
                    user_input.fish.growth_stage,
                    user_input.fish.fish_age_days,
                    user_input.fish.fish_count,
                    user_input.fish.biomass_kg,
                    user_input.fish.average_fish_weight_g,
                ),
            )

            # 3. Log feeding event
            cur.execute(
                """
                INSERT INTO feeding_logs (
                    pond_id, feed_quantity_kg, meal_count, feed_quality_score
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    pond_id,
                    rec.optimization.optimized_daily_feed_kg,
                    rec.optimization.number_of_meals,
                    user_input.feeding.feed_quality_score,
                ),
            )

            # 4. Save recommendation
            base_feed = rec.optimization.baseline_comparison.baseline_feed_kg if rec.optimization.baseline_comparison else 0.0
            cost_saved = rec.optimization.baseline_comparison.cost_saved_usd if rec.optimization.baseline_comparison else 0.0

            cur.execute(
                """
                INSERT INTO recommendations (
                    pond_id, recommended_feed_kg, optimized_feed_kg, expected_waste_kg,
                    waste_risk_score, waste_risk_level, pollution_risk_score, pollution_risk_level,
                    number_of_meals, meal_schedule_json, explanation_summary,
                    baseline_feed_kg, cost_saved_usd
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pond_id,
                    rec.feed_prediction.recommended_daily_feed_kg,
                    rec.optimization.optimized_daily_feed_kg,
                    rec.waste_prediction.expected_waste_kg,
                    rec.waste_prediction.risk_score,
                    rec.waste_prediction.risk_level,
                    rec.pollution_risk.risk_score,
                    rec.pollution_risk.risk_level,
                    rec.optimization.number_of_meals,
                    schedule_json,
                    rec.explanation.summary,
                    base_feed,
                    cost_saved,
                ),
            )
            rec_id = cur.lastrowid
            logger.info("Saved recommendation #%d for pond '%s'", rec_id, pond_id)
            return rec_id

    def get_pond_history(self, pond_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent recommendations and conditions for a given pond."""
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT r.*, w.water_temperature_c, w.dissolved_oxygen_mg_l, w.ammonia_mg_l,
                       f.species, f.biomass_kg
                FROM recommendations r
                LEFT JOIN water_measurements w ON w.pond_id = r.pond_id AND w.id = r.id
                LEFT JOIN fish_stocks f ON f.pond_id = r.pond_id AND f.id = r.id
                WHERE r.pond_id = ?
                ORDER BY r.recorded_at DESC
                LIMIT ?
                """,
                (pond_id, limit),
            )
            rows = [dict(r) for r in cur.fetchall()]
            for row in rows:
                if "meal_schedule_json" in row and isinstance(row["meal_schedule_json"], str):
                    try:
                        row["meal_schedule"] = json.loads(row["meal_schedule_json"])
                    except Exception:
                        row["meal_schedule"] = []
            return rows

    def seed_default_ponds_if_empty(self):
        """Populate database with default demonstration ponds and 7-day history."""
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) as cnt FROM ponds")
            count = cur.fetchone()["cnt"]
            if count > 0:
                return

            demo_ponds = [
                ("pond_01", "Pond 1 (Tilapia Grow-out)", 500.0, "Sector Alpha"),
                ("pond_02", "Pond 2 (Carp Intensive)", 450.0, "Sector Beta"),
                ("pond_03", "Pond 3 (Salmon Coldwater)", 600.0, "Sector Gamma"),
            ]
            for pid, name, vol, loc in demo_ponds:
                cur.execute(
                    "INSERT INTO ponds (pond_id, name, volume_m3, location) VALUES (?, ?, ?, ?)",
                    (pid, name, vol, loc),
                )

            # Insert sample historical readings for Pond 1
            sample_history = [
                (27.2, 6.8, 7.5, 0.020, 5.18, 5.0, 0.25, 2, 2, "2026-10-02 08:00:00"),
                (27.5, 6.6, 7.4, 0.025, 5.07, 5.0, 0.28, 2, 2, "2026-10-03 08:00:00"),
                (27.1, 6.5, 7.5, 0.030, 5.17, 5.2, 0.30, 2, 2, "2026-10-04 08:00:00"),
                (27.8, 6.1, 7.3, 0.035, 5.15, 5.1, 0.32, 2, 2, "2026-10-05 08:00:00"),
                (28.4, 5.5, 7.2, 0.055, 5.06, 5.0, 0.40, 2, 56, "2026-10-06 08:00:00"),
                (27.9, 5.9, 7.3, 0.045, 5.18, 5.1, 0.35, 2, 2, "2026-10-07 08:00:00"),
            ]
            for temp, do, ph, amm, feed, opt_feed, waste, wrisk, prisk, dt in sample_history:
                cur.execute(
                    "INSERT INTO water_measurements (pond_id, water_temperature_c, dissolved_oxygen_mg_l, ph, ammonia_mg_l, nitrate_mg_l, turbidity, recorded_at) VALUES (?, ?, ?, ?, ?, 20.0, 15.0, ?)",
                    ("pond_01", temp, do, ph, amm, dt),
                )
                cur.execute(
                    "INSERT INTO fish_stocks (pond_id, species, growth_stage, fish_age_days, fish_count, biomass_kg, average_fish_weight_g, recorded_at) VALUES (?, 'Tilapia', 'Grow-out', 185, 1660, 250.0, 150.0, ?)",
                    ("pond_01", dt),
                )
                cur.execute(
                    "INSERT INTO feeding_logs (pond_id, feed_quantity_kg, meal_count, feed_quality_score, recorded_at) VALUES (?, ?, 2, 82.0, ?)",
                    ("pond_01", opt_feed, dt),
                )
                cur.execute(
                    """
                    INSERT INTO recommendations (
                        pond_id, recommended_feed_kg, optimized_feed_kg, expected_waste_kg,
                        waste_risk_score, waste_risk_level, pollution_risk_score, pollution_risk_level,
                        number_of_meals, meal_schedule_json, explanation_summary,
                        baseline_feed_kg, cost_saved_usd, recorded_at
                    ) VALUES (?, ?, ?, ?, ?, 'LOW', ?, 'LOW', 2, '[]', 'Historical demo entry', 6.25, 2.50, ?)
                    """,
                    ("pond_01", feed, opt_feed, waste, wrisk, prisk, dt),
                )
            logger.info("Seeded default ponds and historical demonstration records.")
