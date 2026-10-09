"""FastAPI REST API routes for AquaNex AI Aquaculture Feeding Optimization."""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Query, status

from backend.app.schemas.recommendation_schema import FinalRecommendationResponse
from backend.app.services.recommendation_service import recommendation_service
from backend.app.database.repository import AquacultureRepository
from backend.app.data.validation import ValidationError
from backend.app.config.settings import settings

logger = logging.getLogger("AquaNexAPI")
router = APIRouter(prefix="/api/v1", tags=["AquaNex Endpoints"])
repository = AquacultureRepository()


@router.get("/health", summary="System Health & Status")
async def health_check():
    """Verify backend health, ML model readiness, and SQLite database connectivity."""
    models_ready = (
        recommendation_service.feed_service.model_wrapper.model is not None
        and recommendation_service.waste_service.model_wrapper.model is not None
        and recommendation_service.pollution_service.ml_wrapper.model is not None
    )
    return {
        "status": "healthy",
        "service": settings.app_name,
        "environment": settings.environment,
        "models_loaded": models_ready,
        "feed_model": type(recommendation_service.feed_service.model_wrapper.model).__name__,
        "waste_model": type(recommendation_service.waste_service.model_wrapper.model).__name__,
        "pollution_model": type(recommendation_service.pollution_service.ml_wrapper.model).__name__,
    }


@router.post(
    "/recommendation",
    response_model=FinalRecommendationResponse,
    summary="Generate AI Feeding Recommendation & Schedule",
)
async def generate_recommendation_endpoint(
    payload: Dict[str, Any],
    persist: bool = Query(True, description="Persist recommendation to SQLite database"),
):
    """
    Accept fish, water quality, and environmental parameters (accepts both Next.js frontend
    flat keys and canonical backend schema), then executes the full ML & SciPy optimization pipeline.
    """
    try:
        recommendation = recommendation_service.generate_recommendation(
            input_data=payload,
            persist=persist,
        )
        return recommendation
    except ValidationError as val_err:
        logger.warning("Input validation failed: %s", val_err)
        raise HTTPException(
            status_code=getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422),
            detail=str(val_err),
        )
    except Exception as exc:
        logger.exception("Unexpected error during recommendation generation: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AquaNex recommendation engine encountered an error: {str(exc)}",
        )


@router.get("/ponds", summary="List Registered Aquaculture Ponds")
async def list_ponds():
    """Retrieve all monitored ponds."""
    try:
        ponds = repository.list_ponds()
        return {"ponds": ponds, "count": len(ponds)}
    except Exception as exc:
        logger.error("Failed to list ponds: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(exc)}",
        )


@router.get("/history/{pond_id}", summary="Get Historical Pond Recommendations")
async def get_pond_history(
    pond_id: str,
    limit: int = Query(10, ge=1, le=100, description="Number of historical records to return"),
):
    """Retrieve past feeding recommendations, water quality conditions, and savings for a specific pond."""
    try:
        history = repository.get_pond_history(pond_id=pond_id, limit=limit)
        return {"pond_id": pond_id, "history": history, "count": len(history)}
    except Exception as exc:
        logger.error("Failed to get pond history for %s: %s", pond_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(exc)}",
        )
