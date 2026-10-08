"""Pond safety limits, biological bounds, and feeding constraints."""

from typing import Tuple, Dict, Any
from backend.app.config.constants import SPECIES_PROFILES, OPTIMIZATION_PARAMS


def get_feeding_bounds(
    predicted_appetite_kg: float,
    biomass_kg: float,
    features: Dict[str, Any],
) -> Tuple[float, float]:
    """Calculate mathematically grounded safe lower and upper feed bounds (kg).

    - Lower bound: Minimum sustenance intake to avoid growth stalling.
    - Upper bound: Safe ingestion capacity without gut overload or hypoxia hazard.
    """
    species = str(features.get("fishSpecies", features.get("species", "Tilapia")))
    profile = SPECIES_PROFILES.get(species, SPECIES_PROFILES["Tilapia"])

    do = float(features.get("dissolvedOxygenMgL", 6.2))
    crit_do = profile["critical_do_mg_l"]

    appetite = max(0.2, predicted_appetite_kg)
    min_fraction = OPTIMIZATION_PARAMS.get("min_feed_fraction", 0.70)
    max_fraction = OPTIMIZATION_PARAMS.get("max_feed_fraction", 1.25)

    f_min = max(0.1, appetite * min_fraction)
    f_max = appetite * max_fraction

    # Absolute biological stomach intake ceiling (rarely exceeds 6% body weight for adults)
    max_stomach_intake = max(0.5, biomass_kg * 0.08)
    f_max = min(f_max, max_stomach_intake)

    # Hypoxia constraint: severely limit feed if oxygen is depleted
    if do < crit_do:
        f_max = min(f_max, appetite * 0.60)
        f_min = min(f_min, f_max * 0.70)

    if f_min > f_max:
        f_min = f_max * 0.85

    return float(f_min), float(f_max)
