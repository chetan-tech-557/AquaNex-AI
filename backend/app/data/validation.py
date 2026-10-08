"""Validation logic for AquaNex AI inputs.

Ensures physical and biological plausibility, preventing impossible values,
handling boundary edge cases, and returning structured diagnostics.
"""

from typing import List, Tuple
from backend.app.schemas.input_schema import FeedingPredictionInput
from backend.app.config.constants import SPECIES_PROFILES, POLLUTION_THRESHOLDS


class ValidationError(Exception):
    """Custom exception raised for unrecoverable validation failures."""
    pass


def validate_input_data(user_input: FeedingPredictionInput) -> Tuple[bool, List[str], List[str]]:
    """Validate user input against aquaculture physical limits and biological boundaries.

    Returns:
        is_valid: bool
        errors: List of unrecoverable invalid input descriptions
        warnings: List of cautionary notices (e.g. stress conditions)
    """
    errors: List[str] = []
    warnings: List[str] = []

    fish = user_input.fish
    water = user_input.water
    feeding = user_input.feeding
    env = user_input.environment

    # Biological physical invariants
    if fish.biomass_kg <= 0:
        errors.append(f"Biomass must be strictly positive (> 0 kg), got {fish.biomass_kg} kg.")
    if fish.average_fish_weight_g <= 0:
        errors.append(f"Average fish weight must be strictly positive (> 0 g), got {fish.average_fish_weight_g} g.")
    if fish.fish_age_days < 1:
        errors.append(f"Fish age must be at least 1 day, got {fish.fish_age_days}.")

    # Water quality invariants
    if water.dissolved_oxygen_mg_l < 0:
        errors.append(f"Dissolved oxygen cannot be negative, got {water.dissolved_oxygen_mg_l} mg/L.")
    if water.ph < 3.0 or water.ph > 11.0:
        errors.append(f"pH {water.ph} is outside plausible aquatic survival bounds [3.0, 11.0].")
    if water.ammonia_mg_l < 0:
        errors.append(f"Ammonia cannot be negative, got {water.ammonia_mg_l} mg/L.")
    if water.water_temperature_c < 0.0 or water.water_temperature_c > 45.0:
        errors.append(f"Water temperature {water.water_temperature_c}°C is outside plausible liquid limits [0, 45].")

    # Feeding invariants
    if feeding.previous_feed_kg < 0:
        errors.append(f"Previous feed quantity cannot be negative, got {feeding.previous_feed_kg} kg.")
    if feeding.recent_average_feed_kg < 0:
        errors.append(f"Recent average feed cannot be negative, got {feeding.recent_average_feed_kg} kg.")
    if feeding.feeding_frequency < 1 or feeding.feeding_frequency > 8:
        errors.append(f"Feeding frequency must be between 1 and 8 meals/day, got {feeding.feeding_frequency}.")
    if feeding.feed_quality_score < 0 or feeding.feed_quality_score > 100:
        errors.append(f"Feed quality score must be between 0 and 100, got {feeding.feed_quality_score}.")

    # Biological warnings for extreme conditions
    profile = SPECIES_PROFILES.get(fish.species, SPECIES_PROFILES["Tilapia"])

    if water.dissolved_oxygen_mg_l < profile["critical_do_mg_l"]:
        warnings.append(
            f"CRITICAL: Dissolved oxygen ({water.dissolved_oxygen_mg_l:.1f} mg/L) is below survival threshold "
            f"({profile['critical_do_mg_l']} mg/L) for {fish.species}. Fish appetite will be severely depressed."
        )
    elif water.dissolved_oxygen_mg_l < profile["min_do_mg_l"]:
        warnings.append(
            f"ALERT: Dissolved oxygen ({water.dissolved_oxygen_mg_l:.1f} mg/L) is suboptimal for {fish.species} "
            f"(target: >= {profile['min_do_mg_l']} mg/L)."
        )

    temp_min, temp_max = profile["temperature_range"]
    if water.water_temperature_c < temp_min or water.water_temperature_c > temp_max:
        warnings.append(
            f"ALERT: Water temperature ({water.water_temperature_c:.1f}°C) is outside optimal range "
            f"[{temp_min}°C - {temp_max}°C] for {fish.species}."
        )

    if water.ammonia_mg_l >= POLLUTION_THRESHOLDS["ammonia_high"]:
        warnings.append(
            f"ALERT: Ammonia ({water.ammonia_mg_l:.3f} mg/L) exceeds safe threshold ({POLLUTION_THRESHOLDS['ammonia_high']} mg/L)."
        )

    if water.turbidity >= POLLUTION_THRESHOLDS["turbidity_high"]:
        warnings.append(
            f"ALERT: Turbidity ({water.turbidity:.1f} NTU) indicates high suspended solids."
        )

    if env.rainfall_mm >= POLLUTION_THRESHOLDS["rainfall_heavy_mm"]:
        warnings.append(
            f"NOTE: Heavy precipitation ({env.rainfall_mm:.1f} mm) increases risk of pond runoff and dilution."
        )

    is_valid = len(errors) == 0
    return is_valid, errors, warnings
