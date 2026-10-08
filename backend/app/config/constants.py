"""Constants and domain reference values for AquaNex AI.

All aquaculture thresholds, species preferences, and optimization parameters
are documented and centralized here to prevent magic numbers across the codebase.
"""

from typing import Dict, Any, List

# Dataset label and scientific disclosures
DATASET_LABEL = "Controlled simulated prototype dataset"
DATASET_DISCLAIMER = (
    "All training, validation, and demonstration rows are controlled simulation data "
    "developed for the Aarambh WCE Hackathon 2026 prototype. "
    "They are not real commercial farm sensor logs; live deployment requires site-specific "
    "water calibration, laboratory feed analysis, and aquaculture specialist supervision."
)

# Supported species and stages
SUPPORTED_SPECIES = ["Tilapia", "Carp", "Salmon", "Trout", "Catfish", "Shrimp"]
SUPPORTED_GROWTH_STAGES = ["Fry", "Fingerling", "Juvenile", "Grow-out", "Adult", "Broodstock"]

# Species-specific biological references
# Temperature in Celsius, dissolved oxygen in mg/L
SPECIES_PROFILES: Dict[str, Dict[str, Any]] = {
    "Tilapia": {
        "optimal_temperature_c": 28.0,
        "temperature_range": (20.0, 34.0),
        "min_do_mg_l": 5.0,
        "critical_do_mg_l": 3.0,
        "optimal_ph_range": (6.5, 8.5),
        "max_ammonia_mg_l": 0.05,
        "max_nitrate_mg_l": 50.0,
        "max_turbidity_ntu": 40.0,
        "default_fcr": 1.4,
    },
    "Carp": {
        "optimal_temperature_c": 24.0,
        "temperature_range": (18.0, 30.0),
        "min_do_mg_l": 5.5,
        "critical_do_mg_l": 3.5,
        "optimal_ph_range": (6.8, 8.2),
        "max_ammonia_mg_l": 0.04,
        "max_nitrate_mg_l": 45.0,
        "max_turbidity_ntu": 35.0,
        "default_fcr": 1.5,
    },
    "Salmon": {
        "optimal_temperature_c": 15.0,
        "temperature_range": (8.0, 18.0),
        "min_do_mg_l": 7.0,
        "critical_do_mg_l": 5.0,
        "optimal_ph_range": (6.5, 8.0),
        "max_ammonia_mg_l": 0.02,
        "max_nitrate_mg_l": 30.0,
        "max_turbidity_ntu": 20.0,
        "default_fcr": 1.2,
    },
    "Trout": {
        "optimal_temperature_c": 15.0,
        "temperature_range": (8.0, 19.0),
        "min_do_mg_l": 7.0,
        "critical_do_mg_l": 5.0,
        "optimal_ph_range": (6.5, 8.0),
        "max_ammonia_mg_l": 0.02,
        "max_nitrate_mg_l": 30.0,
        "max_turbidity_ntu": 20.0,
        "default_fcr": 1.2,
        "ml_species_alias": "Salmon",
    },
    "Catfish": {
        "optimal_temperature_c": 28.0,
        "temperature_range": (20.0, 32.0),
        "min_do_mg_l": 4.5,
        "critical_do_mg_l": 2.5,
        "optimal_ph_range": (6.5, 8.5),
        "max_ammonia_mg_l": 0.05,
        "max_nitrate_mg_l": 50.0,
        "max_turbidity_ntu": 50.0,
        "default_fcr": 1.5,
        "ml_species_alias": "Carp",
    },
    "Shrimp": {
        "optimal_temperature_c": 29.0,
        "temperature_range": (24.0, 33.0),
        "min_do_mg_l": 5.0,
        "critical_do_mg_l": 3.0,
        "optimal_ph_range": (7.5, 8.5),
        "max_ammonia_mg_l": 0.03,
        "max_nitrate_mg_l": 40.0,
        "max_turbidity_ntu": 30.0,
        "default_fcr": 1.3,
        "ml_species_alias": "Tilapia",
    },
}

# Baseline feeding rates as percentage of biomass per day by growth stage
# Traditional static feeding charts rely purely on these stage rates without environmental adaptation.
BASELINE_STAGE_RATES: Dict[str, float] = {
    "Fry": 0.08,        # 8% of body weight/day
    "Fingerling": 0.05, # 5% of body weight/day
    "Juvenile": 0.04,   # 4% of body weight/day
    "Grow-out": 0.025,  # 2.5% of body weight/day
    "Adult": 0.015,     # 1.5% of body weight/day
    "Broodstock": 0.012,# 1.2% of body weight/day
}


# Environmental and water quality pollution thresholds
POLLUTION_THRESHOLDS: Dict[str, float] = {
    "ammonia_warning": 0.03,
    "ammonia_high": 0.05,
    "ammonia_critical": 0.08,
    "nitrate_warning": 40.0,
    "nitrate_high": 60.0,
    "turbidity_warning": 25.0,
    "turbidity_high": 45.0,
    "do_low": 4.5,
    "do_critical": 3.0,
    "ph_min_acceptable": 6.0,
    "ph_max_acceptable": 9.0,
    "rainfall_heavy_mm": 50.0,
}

# Economic & optimization penalty coefficients
OPTIMIZATION_PARAMS: Dict[str, float] = {
    "feed_cost_per_kg": 2.00,       # USD / kg of standard aquafeed
    "waste_penalty_per_kg": 12.00,   # Cost of unconsumed feed decomposing in water
    "pollution_penalty_weight": 0.15,# Weight on pollution risk score in objective function
    "meal_complexity_penalty": 0.10, # Slight cost for excessive feeding operations
    "min_feed_fraction": 0.70,      # Minimum % of appetite required to maintain welfare
    "max_feed_fraction": 1.25,      # Maximum % of appetite allowed
}

# Standard meal time presets based on meal frequency
MEAL_SCHEDULE_PRESETS: Dict[int, List[str]] = {
    1: ["09:00 AM"],
    2: ["08:30 AM", "05:00 PM"],
    3: ["08:00 AM", "01:00 PM", "06:00 PM"],
    4: ["07:30 AM", "11:30 AM", "03:30 PM", "07:00 PM"],
    5: ["07:00 AM", "10:00 AM", "01:00 PM", "04:30 PM", "07:30 PM"],
}
