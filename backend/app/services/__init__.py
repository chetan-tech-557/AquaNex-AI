"""Services package for AquaNex AI."""

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
