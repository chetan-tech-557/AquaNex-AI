"""Data preprocessing pipeline for AquaNex AI.

Maintains strict consistency between training preprocessing and inference preprocessing.
Features categorical one-hot encoding, imputation, and column ordering.
"""

from typing import List, Dict, Any, Tuple, Union
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from backend.app.config.constants import SUPPORTED_SPECIES, SUPPORTED_GROWTH_STAGES
from backend.app.data.feature_engineering import engineer_features_dict

NUMERICAL_FEATURE_NAMES: List[str] = [
    "temperatureC",
    "dissolvedOxygenMgL",
    "pH",
    "ammoniaMgL",
    "nitrateMgL",
    "turbidityNtu",
    "salinityPpt",
    "fishAgeDays",
    "biomassKg",
    "averageFishWeightG",
    "previousFeedKg",
    "recentAverageFeedKg",
    "feedingFrequency",
    "feedQualityScore",
    "feed_to_biomass_ratio",
    "biomass_per_fish",
    "temperature_deviation",
    "do_stress_indicator",
    "ammonia_stress_indicator",
    "recent_feeding_trend",
    "feed_quality_factor",
    "rainfallMm",
    "humidityPercent",
    "airTemperatureC",
]


class AquaNexPreprocessor(BaseEstimator, TransformerMixin):
    """Production preprocessor for tabular aquaculture data.

    Transforms engineered raw dictionaries/DataFrames into encoded, ordered feature vectors.
    """

    def __init__(self):
        self.numerical_cols = NUMERICAL_FEATURE_NAMES
        self.species_list = list(SUPPORTED_SPECIES)
        self.stages_list = list(SUPPORTED_GROWTH_STAGES)
        self.feature_names_out_: List[str] = []

    def fit(self, X: pd.DataFrame, y=None) -> "AquaNexPreprocessor":
        """Fit preprocessor and establish output feature names."""
        names = list(self.numerical_cols)
        for sp in self.species_list:
            names.append(f"species_{sp}")
        for st in self.stages_list:
            names.append(f"stage_{st}")
        self.feature_names_out_ = names
        return self

    def transform(self, X: Union[pd.DataFrame, List[Dict[str, Any]]]) -> np.ndarray:
        """Transform input data into numeric matrix matching fitted columns."""
        if isinstance(X, pd.DataFrame):
            records = X.to_dict(orient="records")
        elif isinstance(X, list):
            records = X
        else:
            records = [X]

        # Engineer features on any records if missing
        processed_records = []
        for r in records:
            if "temperature_deviation" not in r:
                r = engineer_features_dict(r)
            processed_records.append(r)

        rows = []
        for r in processed_records:
            row_vals = []
            # 1. Numerical features
            for col in self.numerical_cols:
                val = r.get(col, 0.0)
                try:
                    val = float(val) if val is not None else 0.0
                except (ValueError, TypeError):
                    val = 0.0
                row_vals.append(val)

            # 2. Species one-hot
            raw_species = str(r.get("fishSpecies", r.get("species", "Tilapia"))).strip().capitalize()
            from backend.app.config.constants import SPECIES_PROFILES
            current_species = SPECIES_PROFILES.get(raw_species, {}).get("ml_species_alias", raw_species)
            for sp in self.species_list:
                row_vals.append(1.0 if current_species == sp else 0.0)

            # 3. Stage one-hot
            raw_stage = str(r.get("growthStage", r.get("growth_stage", "Grow-out"))).strip()
            stage_aliases = {
                "fingerling": "Fry",
                "broodstock": "Adult",
                "brood": "Adult",
                "growout": "Grow-out",
                "grow-out": "Grow-out",
                "fry": "Fry",
                "juvenile": "Juvenile",
                "adult": "Adult",
            }
            current_stage = stage_aliases.get(raw_stage.lower(), raw_stage.capitalize())
            for st in self.stages_list:
                row_vals.append(1.0 if current_stage == st else 0.0)

            rows.append(row_vals)

        return np.array(rows, dtype=np.float64)

    def get_feature_names_out(self, input_features=None) -> List[str]:
        """Return list of transformed feature names."""
        if not self.feature_names_out_:
            self.fit(pd.DataFrame())
        return list(self.feature_names_out_)
