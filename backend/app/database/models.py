"""Database entity representations for AquaNex AI."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PondEntity:
    pond_id: str
    name: str
    volume_m3: float = 500.0
    location: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class RecommendationEntity:
    id: Optional[int]
    pond_id: str
    recommended_feed_kg: float
    optimized_feed_kg: float
    expected_waste_kg: float
    waste_risk_score: int
    waste_risk_level: str
    pollution_risk_score: int
    pollution_risk_level: str
    number_of_meals: int
    meal_schedule_json: str
    explanation_summary: str
    baseline_feed_kg: float
    cost_saved_usd: float
    recorded_at: Optional[str] = None
