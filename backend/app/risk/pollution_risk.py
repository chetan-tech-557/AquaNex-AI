"""Scientific multi-parameter pond pollution and environmental risk engine.

Evaluates water chemistry, decaying feed waste accumulation, and environmental factors
using transparent, configurable domain thresholds and weighted risk indicators.
"""

from typing import Dict, Any, List, Tuple
from backend.app.config.constants import POLLUTION_THRESHOLDS, SPECIES_PROFILES


def evaluate_pollution_risk(
    features: Dict[str, Any],
    feed_kg: float,
    expected_waste_kg: float,
) -> Tuple[int, str, List[str], Dict[str, float], str]:
    """Calculate multi-criteria pollution risk score and diagnostic factors.

    Components evaluated:
    1. Dissolved Oxygen Stress (weight: 25%)
    2. Ammonia Toxicity (weight: 30%)
    3. Turbidity / Suspended Solids (weight: 15%)
    4. Nitrate Buildup (weight: 10%)
    5. pH Aberration (weight: 10%)
    6. Decaying Feed Waste Burden (weight: 10%)
    """
    contributing_factors: List[str] = []
    sub_scores: Dict[str, float] = {}

    species = str(features.get("fishSpecies", features.get("species", "Tilapia")))
    profile = SPECIES_PROFILES.get(species, SPECIES_PROFILES["Tilapia"])

    do = float(features.get("dissolvedOxygenMgL", 6.2))
    ammonia = float(features.get("ammoniaMgL", 0.025))
    nitrate = float(features.get("nitrateMgL", 22.0))
    turbidity = float(features.get("turbidityNtu", 14.0))
    ph = float(features.get("pH", 7.4))
    rainfall = float(features.get("rainfallMm", 8.0))

    # 1. Dissolved Oxygen Sub-score (0-100)
    # Severe oxygen depletion accelerates anaerobic decay and microbial pollution
    crit_do = profile["critical_do_mg_l"]
    min_do = profile["min_do_mg_l"]
    if do < crit_do:
        do_score = 100.0
        contributing_factors.append(
            f"Critically low dissolved oxygen ({do:.2f} mg/L < {crit_do} mg/L) induces severe hypoxia and microbial stress."
        )
    elif do < min_do:
        do_score = 30.0 + 70.0 * (min_do - do) / max(0.1, min_do - crit_do)
        contributing_factors.append(
            f"Depressed dissolved oxygen ({do:.2f} mg/L) is below safe minimum ({min_do} mg/L)."
        )
    else:
        do_score = max(0.0, 15.0 * (min_do - do) / max(0.1, min_do))
    sub_scores["dissolved_oxygen"] = round(do_score, 1)

    # 2. Ammonia Sub-score (0-100)
    # Total Ammonia Nitrogen: highly toxic in un-ionized form
    crit_amm = POLLUTION_THRESHOLDS["ammonia_critical"]
    high_amm = POLLUTION_THRESHOLDS["ammonia_high"]
    warn_amm = POLLUTION_THRESHOLDS["ammonia_warning"]

    if ammonia >= crit_amm:
        amm_score = 100.0
        contributing_factors.append(
            f"Critical ammonia concentration ({ammonia:.3f} mg/L >= {crit_amm} mg/L) poses severe ecotoxic hazard."
        )
    elif ammonia >= high_amm:
        amm_score = 70.0 + 30.0 * (ammonia - high_amm) / max(0.001, crit_amm - high_amm)
        contributing_factors.append(
            f"Elevated ammonia ({ammonia:.3f} mg/L) exceeds safe threshold ({high_amm} mg/L)."
        )
    elif ammonia >= warn_amm:
        amm_score = 30.0 + 40.0 * (ammonia - warn_amm) / max(0.001, high_amm - warn_amm)
        contributing_factors.append(
            f"Ammonia ({ammonia:.3f} mg/L) is approaching cautionary limits."
        )
    else:
        amm_score = max(0.0, 30.0 * (ammonia / max(0.001, warn_amm)))
    sub_scores["ammonia"] = round(amm_score, 1)

    # 3. Turbidity Sub-score (0-100)
    high_turb = POLLUTION_THRESHOLDS["turbidity_high"]
    warn_turb = POLLUTION_THRESHOLDS["turbidity_warning"]
    if turbidity >= high_turb:
        turb_score = min(100.0, 75.0 + 25.0 * (turbidity - high_turb) / 30.0)
        contributing_factors.append(
            f"High turbidity ({turbidity:.1f} NTU) indicates excessive suspended organic sediment or algal bloom."
        )
    elif turbidity >= warn_turb:
        turb_score = 35.0 + 40.0 * (turbidity - warn_turb) / max(1.0, high_turb - warn_turb)
        contributing_factors.append(
            f"Turbidity ({turbidity:.1f} NTU) is moderately elevated against the {warn_turb} NTU threshold."
        )
    else:
        turb_score = max(0.0, 35.0 * (turbidity / max(1.0, warn_turb)))
    sub_scores["turbidity"] = round(turb_score, 1)

    # 4. Nitrate Sub-score (0-100)
    high_nit = POLLUTION_THRESHOLDS["nitrate_high"]
    warn_nit = POLLUTION_THRESHOLDS["nitrate_warning"]
    if nitrate >= high_nit:
        nit_score = min(100.0, 70.0 + 30.0 * (nitrate - high_nit) / 40.0)
        contributing_factors.append(
            f"High nitrate concentration ({nitrate:.1f} mg/L) signals long-term nutrient accumulation."
        )
    elif nitrate >= warn_nit:
        nit_score = 30.0 + 40.0 * (nitrate - warn_nit) / max(1.0, high_nit - warn_nit)
    else:
        nit_score = max(0.0, 30.0 * (nitrate / max(1.0, warn_nit)))
    sub_scores["nitrate"] = round(nit_score, 1)

    # 5. pH Sub-score (0-100)
    ph_min, ph_max = profile["optimal_ph_range"]
    if ph < POLLUTION_THRESHOLDS["ph_min_acceptable"]:
        ph_score = 80.0
        contributing_factors.append(f"Acidic water pH ({ph:.2f}) destabilizes biofilter nitrification.")
    elif ph > POLLUTION_THRESHOLDS["ph_max_acceptable"]:
        ph_score = 85.0
        contributing_factors.append(f"Alkaline water pH ({ph:.2f}) drastically increases toxic free-ammonia ratio.")
    elif ph < ph_min or ph > ph_max:
        ph_score = 35.0
    else:
        ph_score = 5.0
    sub_scores["ph"] = round(ph_score, 1)

    # 6. Decaying Feed Waste Sub-score (0-100)
    waste_ratio = expected_waste_kg / max(0.1, feed_kg)
    waste_score = min(100.0, waste_ratio * 400.0)
    if expected_waste_kg > 1.0:
        contributing_factors.append(
            f"Estimated uneaten feed ({expected_waste_kg:.2f} kg) contributes substantial organic biological oxygen demand (BOD)."
        )
    sub_scores["feed_waste_burden"] = round(waste_score, 1)

    # Rainfall context
    if rainfall >= POLLUTION_THRESHOLDS["rainfall_heavy_mm"]:
        contributing_factors.append(
            f"Heavy rainfall ({rainfall:.1f} mm/day) introduces external agricultural runoff risk."
        )

    # Weighted aggregate score
    weights = {
        "dissolved_oxygen": 0.25,
        "ammonia": 0.30,
        "turbidity": 0.15,
        "nitrate": 0.10,
        "ph": 0.10,
        "feed_waste_burden": 0.10,
    }
    agg_score = sum(sub_scores[k] * weights[k] for k in weights)

    # If ammonia or DO is critical, risk floor is automatically high
    if ammonia >= crit_amm or do < crit_do:
        agg_score = max(agg_score, 85.0)

    final_score = int(round(max(0.0, min(100.0, agg_score))))

    if final_score >= 65:
        tier = "HIGH"
        mitigation = "Activate emergency pond aerators, reduce feeding ration by 30-50%, and schedule a 20% water exchange."
    elif final_score >= 35:
        tier = "MEDIUM"
        mitigation = "Increase mechanical aeration during feeding windows, verify biofilter function, and closely monitor unconsumed pellets."
    else:
        tier = "LOW"
        mitigation = "Water quality parameters are within safe target ranges. Maintain standard scheduled rations and monitoring."

    if not contributing_factors:
        contributing_factors.append("All measured water quality and waste parameters are within standard baseline thresholds.")

    return final_score, tier, contributing_factors, sub_scores, mitigation
