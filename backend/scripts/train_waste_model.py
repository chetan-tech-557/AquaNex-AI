"""Model training script for feed waste prediction.

Trains regression model on `estimatedWasteKg` to predict expected uneaten feed
based on feeding intensity, water conditions, temperature stress, and feed quality.
"""

import sys
import json
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

from backend.app.config.settings import settings
from backend.app.data.preprocessing import AquaNexPreprocessor
from backend.app.data.feature_engineering import engineer_features_dataframe

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TrainWasteModel")


def train_waste_model():
    data_path = settings.raw_data_path
    if not data_path.exists():
        raise FileNotFoundError(f"Raw dataset not found at {data_path}")

    logger.info("Loading dataset from %s", data_path)
    df = pd.read_csv(data_path)

    target_col = "estimatedWasteKg"
    if target_col not in df.columns:
        raise ValueError(f"Waste target column '{target_col}' not in dataset.")

    df_engineered = engineer_features_dataframe(df)
    preprocessor = AquaNexPreprocessor()
    preprocessor.fit(df_engineered)
    X = preprocessor.transform(df_engineered)
    y = df_engineered[target_col].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )

    candidates = {}

    logger.info("Training Candidate A: Random Forest Regressor for Waste...")
    rf = RandomForestRegressor(n_estimators=45, max_depth=8, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)
    candidates["Random Forest Regressor"] = {
        "model": rf,
        "mae": float(mean_absolute_error(y_test, rf_pred)),
        "rmse": float(root_mean_squared_error(y_test, rf_pred)),
        "r2": float(r2_score(y_test, rf_pred)),
    }

    logger.info("Training Candidate B: Gradient Boosting Regressor for Waste...")
    gb = GradientBoostingRegressor(n_estimators=50, learning_rate=0.08, max_depth=4, random_state=42)
    gb.fit(X_train, y_train)
    gb_pred = gb.predict(X_test)
    candidates["Gradient Boosting Regressor"] = {
        "model": gb,
        "mae": float(mean_absolute_error(y_test, gb_pred)),
        "rmse": float(root_mean_squared_error(y_test, gb_pred)),
        "r2": float(r2_score(y_test, gb_pred)),
    }

    best_name = min(candidates.keys(), key=lambda k: candidates[k]["rmse"])
    best_info = candidates[best_name]
    best_model = best_info["model"]

    logger.info("=== WASTE MODEL EVALUATION ===")
    for name, c in candidates.items():
        logger.info("%-28s -> MAE: %.4f kg | RMSE: %.4f kg | R²: %.4f", name, c["mae"], c["rmse"], c["r2"])
    logger.info("Selected Waste Model: %s (RMSE: %.4f)", best_name, best_info["rmse"])

    settings.trained_models_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, settings.waste_model_path)
    logger.info("Saved waste model to %s", settings.waste_model_path)

    waste_pipeline_path = settings.trained_models_dir / "waste_pipeline.joblib"
    joblib.dump(preprocessor, waste_pipeline_path)

    return best_model, preprocessor, best_info


if __name__ == "__main__":
    train_waste_model()
