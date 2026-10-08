"""Feed waste risk evaluation and reason attribution."""

from typing import List, Tuple, Dict, Any
from backend.app.config.constants import SPECIES_PROFILES


def evaluate_waste_risk(
    feed_kg: float,
    expected_waste_kg: float,
    features: Dict[str, Any],
) -> Tuple[int, str, List[str]]:
    """Determine waste risk score (0-100), risk tier (LOW/MEDIUM/HIGH), and diagnostic reasons.

    Waste risk rises when:
    - Temperature deviates significantly from species optimum (metabolic slowing)
    - Dissolved oxygen is depressed (fish refuse feed)
    - Feed quality score is poor (crumbles before consumption)
    - Prior feeding was abnormally high relative to appetite
    """
    reasons: List[str] = []

    waste_ratio = expected_waste_kg / max(0.1, feed_kg)
    # Base score on waste percentage
    base_score = int(min(100.0, waste_ratio * 350.0))

    species = str(features.get("fishSpecies", features.get("species", "Tilapia")))
    profile = SPECIES_PROFILES.get(species, SPECIES_PROFILES["Tilapia"])

    temp = float(features.get("temperatureC", 27.0))
    optimal_temp = profile["optimal_temperature_c"]
    temp_diff = abs(temp - optimal_temp)

    if temp_diff >= 3.5:
        reasons.append(
            f"Water temperature ({temp:.1f}°C) is {temp_diff:.1f}°C away from {species} optimum ({optimal_temp:.1f}°C), suppressing appetite."
        )
        base_score = max(base_score, 45)

    do = float(features.get("dissolvedOxygenMgL", 6.2))
    if do < profile["critical_do_mg_l"]:
        reasons.append(
            f"Critically low dissolved oxygen ({do:.1f} mg/L < {profile['critical_do_mg_l']} mg/L) causes severe feeding cessation."
        )
        base_score = max(base_score, 70)
    elif do < profile["min_do_mg_l"]:
        reasons.append(
            f"Suboptimal dissolved oxygen ({do:.1f} mg/L) reduces feeding vigor."
        )
        base_score = max(base_score, 40)

    quality = float(features.get("feedQualityScore", 82.0))
    if quality < 55.0:
        reasons.append(
            f"Low feed quality index ({quality:.0f}/100) causes rapid pellet disintegration and fines."
        )
        base_score = max(base_score, 50)
    elif quality < 70.0:
        reasons.append(
            f"Moderate feed quality index ({quality:.0f}/100) increases uneaten sediment."
        )

    prev_feed = float(features.get("previousFeedKg", 5.0))
    recent_avg = float(features.get("recentAverageFeedKg", 5.2))
    if prev_feed > recent_avg * 1.25 and prev_feed > 3.0:
        reasons.append(
            f"Previous feed ({prev_feed:.1f} kg) was substantially higher than recent average ({recent_avg:.1f} kg), indicating potential overfeeding."
        )

    # Classify tier
    score = int(max(0, min(100, base_score)))
    if score >= 65:
        tier = "HIGH"
    elif score >= 30:
        tier = "MEDIUM"
    else:
        tier = "LOW"

    if not reasons and tier == "LOW":
        reasons.append("Feeding efficiency is in the optimal range with minimal expected pellet loss.")

    return score, tier, reasons
