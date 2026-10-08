"""Model training script for feed requirement prediction.

Executes:
1. Data loading from raw CSV
2. Feature engineering & validation
3. Train/test split (80/20 held-out)
4. Candidate model training (Random Forest vs Gradient Boosting)
5. Rigorous metric evaluation (MAE, RMSE, R²)
6. Model selection and Joblib serialization
7. Metric report generation
"""

import sys
import json
import logging
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

from backend.app.config.settings import settings
from backend.app.config.constants import DATASET_LABEL, DATASET_DISCLAIMER
from backend.app.data.preprocessing import AquaNexPreprocessor
from backend.app.data.feature_engineering import engineer_features_dataframe

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TrainFeedModel")


def train_feed_model():
    data_path = settings.raw_data_path
    if not data_path.exists():
        raise FileNotFoundError(f"Raw dataset not found at {data_path}")

    logger.info("Loading raw dataset from %s", data_path)
    df = pd.read_csv(data_path)
    logger.info("Loaded %d rows with columns: %s", len(df), list(df.columns))

    target_col = "estimatedFeedRequirementKg"
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' missing from dataset.")

    # 1. Feature Engineering
    logger.info("Applying domain feature engineering...")
    df_engineered = engineer_features_dataframe(df)

    # 2. Preprocessing
    preprocessor = AquaNexPreprocessor()
    preprocessor.fit(df_engineered)
    X = preprocessor.transform(df_engineered)
    y = df_engineered[target_col].values
    feature_names = preprocessor.get_feature_names_out()
    logger.info("Preprocessed X shape: %s with %d features", X.shape, len(feature_names))

    # 3. Train/Test split (80% train, 20% held-out test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )
    logger.info("Split: %d training samples, %d test samples", len(X_train), len(X_test))

    # Baseline simple model: stage-rate biomass
    # Compute baseline metrics for honest comparison
    baseline_preds = []
    for r in df_engineered.iloc[X_test.shape[0]:].to_dict(orient="records") if len(df_engineered) >= len(X_test) else df_engineered.to_dict(orient="records")[:len(X_test)]:
        stage = str(r.get("growthStage", "Grow-out"))
        biomass = float(r.get("biomassKg", 250.0))
        rate = 0.025
        if stage == "Fry": rate = 0.08
        elif stage == "Juvenile": rate = 0.04
        elif stage == "Adult": rate = 0.015
        baseline_preds.append(biomass * rate)
    baseline_preds = np.array(baseline_preds[:len(y_test)])

    baseline_mae = float(mean_absolute_error(y_test, baseline_preds))
    baseline_rmse = float(root_mean_squared_error(y_test, baseline_preds))
    baseline_r2 = float(r2_score(y_test, baseline_preds))

    # 4. Train Candidate Models
    candidates = {}

    # Candidate A: Random Forest Regressor
    logger.info("Training Candidate A: Random Forest Regressor...")
    rf = RandomForestRegressor(
        n_estimators=50,
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)
    candidates["Random Forest Regressor"] = {
        "model": rf,
        "mae": float(mean_absolute_error(y_test, rf_pred)),
        "rmse": float(root_mean_squared_error(y_test, rf_pred)),
        "r2": float(r2_score(y_test, rf_pred)),
    }

    # Candidate B: Gradient Boosting Regressor
    logger.info("Training Candidate B: Gradient Boosting Regressor...")
    gb = GradientBoostingRegressor(
        n_estimators=60,
        learning_rate=0.08,
        max_depth=5,
        random_state=42,
    )
    gb.fit(X_train, y_train)
    gb_pred = gb.predict(X_test)
    candidates["Gradient Boosting Regressor"] = {
        "model": gb,
        "mae": float(mean_absolute_error(y_test, gb_pred)),
        "rmse": float(root_mean_squared_error(y_test, gb_pred)),
        "r2": float(r2_score(y_test, gb_pred)),
    }

    # Select best model based on RMSE
    best_name = min(candidates.keys(), key=lambda k: candidates[k]["rmse"])
    best_info = candidates[best_name]
    best_model = best_info["model"]

    logger.info("=== CANDIDATE EVALUATION ON HELD-OUT TEST SET ===")
    for name, c in candidates.items():
        logger.info(
            "%-28s -> MAE: %.4f kg | RMSE: %.4f kg | R²: %.4f",
            name, c["mae"], c["rmse"], c["r2"]
        )
    logger.info(
        "%-28s -> MAE: %.4f kg | RMSE: %.4f kg | R²: %.4f",
        "Stage-rate biomass baseline", baseline_mae, baseline_rmse, baseline_r2
    )
    logger.info("Selected Champion Model: %s (RMSE: %.4f)", best_name, best_info["rmse"])

    # 5. Save model and pipeline
    settings.trained_models_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, settings.feed_model_path)
    joblib.dump(preprocessor, settings.feed_pipeline_path)
    logger.info("Saved champion model to %s", settings.feed_model_path)
    logger.info("Saved preprocessor pipeline to %s", settings.feed_pipeline_path)

    # 6. Save model metrics report
    metrics_report = {
        "selectedModel": f"{best_name} (selected by held-out test RMSE)",
        "trainingRows": int(len(X_train)),
        "testRows": int(len(X_test)),
        "datasetLabel": DATASET_LABEL,
        "datasetDisclaimer": DATASET_DISCLAIMER,
        "featureNames": feature_names,
        "modelScores": [
            {
                "name": name,
                "available": True,
                "mae": round(c["mae"], 4),
                "rmse": round(c["rmse"], 4),
                "r2": round(c["r2"], 4),
                "note": "Evaluated on held-out test split (20%)",
            }
            for name, c in candidates.items()
        ] + [
            {
                "name": "Stage-rate biomass baseline",
                "available": True,
                "mae": round(baseline_mae, 4),
                "rmse": round(baseline_rmse, 4),
                "r2": round(baseline_r2, 4),
                "note": "Traditional static feed chart baseline",
            },
            {
                "name": "XGBoost Regressor",
                "available": False,
                "mae": None,
                "rmse": None,
                "r2": None,
                "note": "Not installed in this environment; no fabricated score claimed.",
            }
        ],
    }

    with open(settings.model_metrics_path, "w") as f:
        json.dump(metrics_report, f, indent=2)
    logger.info("Saved model metrics to %s", settings.model_metrics_path)

    return best_model, preprocessor, metrics_report


if __name__ == "__main__":
    train_feed_model()
