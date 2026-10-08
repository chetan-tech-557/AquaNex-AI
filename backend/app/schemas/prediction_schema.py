"""Prediction result schemas for feed requirement, feed waste, and pollution risk."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class FeedPredictionResult(BaseModel):
    """Output of ML feed requirement estimation."""

    recommended_daily_feed_kg: float = Field(
        ...,
        description="Model predicted daily feed requirement in kilograms",
    )
    model_name: str = Field(
        ...,
        description="Name of the regression model producing this prediction",
    )
    confidence_or_uncertainty: float = Field(
        default=0.95,
        description="Estimated confidence score or prediction interval width",
    )
    unadjusted_ml_feed_kg: Optional[float] = Field(
        default=None,
        description="Raw regression output before ecological bounds and safety caps",
    )
    applied_cap: Optional[str] = Field(
        default=None,
        description="Description of any ecological guard or stress cap applied",
    )


class WastePredictionResult(BaseModel):
    """Output of feed waste estimation and risk categorization."""

    expected_waste_kg: float = Field(
        ...,
        description="Predicted uneaten or unassimilated feed in kilograms",
    )
    waste_percentage: float = Field(
        ...,
        description="Expected waste as a percentage of total feed fed",
    )
    risk_level: str = Field(
        ...,
        description="Waste risk categorization: LOW, MEDIUM, or HIGH",
    )
    risk_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Waste risk index score between 0 and 100",
    )
    contributing_reasons: List[str] = Field(
        default_factory=list,
        description="Key diagnostic factors driving the expected waste",
    )


class PollutionRiskResult(BaseModel):
    """Output of environmental and pond water pollution risk analysis."""

    risk_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Aggregate pond water pollution index score (0-100)",
    )
    risk_level: str = Field(
        ...,
        description="Pollution risk tier: LOW, MEDIUM, or HIGH",
    )
    contributing_factors: List[str] = Field(
        default_factory=list,
        description="Specific water quality deviations or stress drivers",
    )
    sub_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Individual component risk scores (ammonia, DO, turbidity, waste)",
    )
    recommended_mitigation: str = Field(
        default="",
        description="Recommended operational intervention (e.g. aeration, water exchange)",
    )
