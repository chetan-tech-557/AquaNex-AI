"""AquaNex AI Backend Application Package."""

from backend.app.services.recommendation_service import (
    AquacultureRecommendationService,
    recommendation_service,
    get_recommendation,
)

__all__ = [
    "AquacultureRecommendationService",
    "recommendation_service",
    "get_recommendation",
]
