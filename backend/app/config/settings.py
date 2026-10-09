"""Application configuration and environment settings for AquaNex AI."""

import os
from pathlib import Path
from pydantic import BaseModel, Field

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
APP_DIR = BASE_DIR / "app"
DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "aquaculture_simulation_data.csv"
TRAINED_MODELS_DIR = BASE_DIR / "trained_models"

FEED_MODEL_PATH = TRAINED_MODELS_DIR / "feed_model.joblib"
WASTE_MODEL_PATH = TRAINED_MODELS_DIR / "waste_model.joblib"
POLLUTION_MODEL_PATH = TRAINED_MODELS_DIR / "pollution_model.joblib"
FEED_PIPELINE_PATH = TRAINED_MODELS_DIR / "feed_pipeline.joblib"
WASTE_PIPELINE_PATH = TRAINED_MODELS_DIR / "waste_pipeline.joblib"
POLLUTION_PIPELINE_PATH = TRAINED_MODELS_DIR / "pollution_pipeline.joblib"
MODEL_METRICS_PATH = TRAINED_MODELS_DIR / "model_metrics.json"

DEFAULT_DB_PATH = BASE_DIR / "aquanex.db"


class Settings(BaseModel):
    """Global system configuration settings."""

    app_name: str = "AquaNex AI Backend"
    environment: str = Field(default_factory=lambda: os.getenv("AQUANEX_ENV", "development"))
    debug: bool = Field(default_factory=lambda: os.getenv("AQUANEX_DEBUG", "True").lower() == "true")
    log_level: str = Field(default_factory=lambda: os.getenv("AQUANEX_LOG_LEVEL", "INFO"))

    # Database
    database_url: str = Field(
        default_factory=lambda: os.getenv("AQUANEX_DB_URL", f"sqlite:///{DEFAULT_DB_PATH.as_posix()}")
    )
    db_path: Path = DEFAULT_DB_PATH

    # Model paths
    feed_model_path: Path = FEED_MODEL_PATH
    waste_model_path: Path = WASTE_MODEL_PATH
    pollution_model_path: Path = POLLUTION_MODEL_PATH
    feed_pipeline_path: Path = FEED_PIPELINE_PATH
    waste_pipeline_path: Path = WASTE_PIPELINE_PATH
    pollution_pipeline_path: Path = POLLUTION_PIPELINE_PATH
    model_metrics_path: Path = MODEL_METRICS_PATH
    raw_data_path: Path = RAW_DATA_PATH
    trained_models_dir: Path = TRAINED_MODELS_DIR


    # Server and CORS settings
    api_host: str = Field(default_factory=lambda: os.getenv("AQUANEX_API_HOST", "0.0.0.0"))
    api_port: int = Field(default_factory=lambda: int(os.getenv("AQUANEX_API_PORT", "8000")))
    cors_origins_raw: str = Field(
        default_factory=lambda: os.getenv(
            "AQUANEX_CORS_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001",
        )
    )

    @property
    def cors_origins(self) -> list:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]


settings = Settings()
