"""Model training and calibration script for pollution risk assessment.

Trains an auxiliary pollution risk score model on `pollutionRiskScore`
while preserving transparent domain rules for multi-parameter risk classification.
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
logger = logging.getLogger("TrainPollutionModel")


def train_pollution_model():
    data_path = settings.raw_data_path
    if not data_path.exists():
        raise FileNotFoundError(f"Raw dataset not found at {data_path}")

    logger.info("Loading dataset from %s", data_path)
    df = pd.read_csv(data_path)

    target_col = "pollutionRiskScore"
    if target_col not in df.columns:
        raise ValueError(f"Pollution risk target column '{target_col}' not in dataset.")

    df_engineered = engineer_features_dataframe(df)
    preprocessor = AquaNexPreprocessor()
    preprocessor.fit(df_engineered)
    X = preprocessor.transform(df_engineered)
    y = df_engineered[target_col].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )

    logger.info("Training Random Forest Regressor for Pollution Risk Score...")
    rf = RandomForestRegressor(n_estimators=40, max_depth=8, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)

    mae = float(mean_absolute_error(y_test, rf_pred))
    rmse = float(root_mean_squared_error(y_test, rf_pred))
    r2 = float(r2_score(y_test, rf_pred))

    logger.info("Pollution Model Evaluated -> MAE: %.2f | RMSE: %.2f | R²: %.4f", mae, rmse, r2)

    settings.trained_models_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(rf, settings.pollution_model_path)
    logger.info("Saved pollution model to %s", settings.pollution_model_path)

    return rf, preprocessor, {"mae": mae, "rmse": rmse, "r2": r2}


if __name__ == "__main__":
    train_pollution_model()
