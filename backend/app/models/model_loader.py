"""Thread-safe singleton model loader for AquaNex AI.

Loads models once into memory rather than retraining or reloading on every inference call.
Provides descriptive diagnostics if files are missing or unreadable.
"""

import logging
import threading
from pathlib import Path
from typing import Any, Optional
import joblib

from backend.app.config.settings import settings

logger = logging.getLogger("ModelLoader")

_lock = threading.Lock()
_models: dict[str, Any] = {}


class ModelLoadError(Exception):
    """Raised when an essential ML artifact fails to load."""
    pass


def _load_joblib_file(path: Path, name: str) -> Any:
    if not path.exists():
        raise ModelLoadError(
            f"{name} artifact not found at '{path.as_posix()}'. "
            f"Please run the training script first: 'python backend/scripts/train_feed_model.py'."
        )
    try:
        obj = joblib.load(path)
        logger.info("Successfully loaded %s from %s", name, path.name)
        return obj
    except Exception as exc:
        raise ModelLoadError(f"Corrupted or incompatible model artifact at '{path.as_posix()}': {exc}") from exc


def get_feed_model() -> Any:
    """Retrieve singleton Feed Requirement Regressor."""
    with _lock:
        if "feed_model" not in _models:
            _models["feed_model"] = _load_joblib_file(settings.feed_model_path, "Feed Model")
        return _models["feed_model"]


def get_feed_pipeline() -> Any:
    """Retrieve singleton Preprocessor Pipeline."""
    with _lock:
        if "feed_pipeline" not in _models:
            _models["feed_pipeline"] = _load_joblib_file(settings.feed_pipeline_path, "Feed Pipeline")
        return _models["feed_pipeline"]


def get_waste_model() -> Any:
    """Retrieve singleton Feed Waste Regressor."""
    with _lock:
        if "waste_model" not in _models:
            _models["waste_model"] = _load_joblib_file(settings.waste_model_path, "Waste Model")
        return _models["waste_model"]


def get_pollution_model() -> Optional[Any]:
    """Retrieve singleton Pollution Model (if available)."""
    with _lock:
        if "pollution_model" not in _models:
            if settings.pollution_model_path.exists():
                _models["pollution_model"] = _load_joblib_file(settings.pollution_model_path, "Pollution Model")
            else:
                _models["pollution_model"] = None
        return _models["pollution_model"]


def clear_model_cache():
    """Clear in-memory cache to force reloading upon new training."""
    with _lock:
        _models.clear()
        logger.info("Model cache cleared.")
