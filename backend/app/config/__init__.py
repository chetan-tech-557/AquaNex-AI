"""Configuration package for AquaNex AI."""

from backend.app.config.settings import settings
from backend.app.config.constants import (
    DATASET_LABEL,
    DATASET_DISCLAIMER,
    SUPPORTED_SPECIES,
    SUPPORTED_GROWTH_STAGES,
    SPECIES_PROFILES,
    BASELINE_STAGE_RATES,
    POLLUTION_THRESHOLDS,
    OPTIMIZATION_PARAMS,
    MEAL_SCHEDULE_PRESETS,
)

__all__ = [
    "settings",
    "DATASET_LABEL",
    "DATASET_DISCLAIMER",
    "SUPPORTED_SPECIES",
    "SUPPORTED_GROWTH_STAGES",
    "SPECIES_PROFILES",
    "BASELINE_STAGE_RATES",
    "POLLUTION_THRESHOLDS",
    "OPTIMIZATION_PARAMS",
    "MEAL_SCHEDULE_PRESETS",
]
