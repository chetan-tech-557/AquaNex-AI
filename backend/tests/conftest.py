import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from backend.app.schemas.input_schema import FeedingPredictionInput


@pytest.fixture
def normal_pond_input():
    """Scenario 1: Normal healthy pond."""
    return FeedingPredictionInput.from_flat_dict({
        "pond_id": "test_normal",
        "fishSpecies": "Tilapia",
        "growthStage": "Grow-out",
        "fishAgeDays": 190,
        "biomassKg": 250.0,
        "averageFishWeightG": 150.0,
        "temperatureC": 27.0,
        "dissolvedOxygenMgL": 6.2,
        "pH": 7.4,
        "ammoniaMgL": 0.025,
        "nitrateMgL": 22.0,
        "turbidityNtu": 14.0,
        "salinityPpt": 0.5,
        "previousFeedKg": 5.0,
        "recentAverageFeedKg": 5.2,
        "feedingFrequency": 2,
        "feedQualityScore": 82.0,
        "rainfallMm": 8.0,
        "humidityPercent": 66.0,
        "airTemperatureC": 25.5,
    })


@pytest.fixture
def low_do_input():
    """Scenario 2: Low dissolved oxygen pond (hypoxia event)."""
    return FeedingPredictionInput.from_flat_dict({
        "pond_id": "test_low_do",
        "fishSpecies": "Tilapia",
        "growthStage": "Grow-out",
        "fishAgeDays": 190,
        "biomassKg": 250.0,
        "averageFishWeightG": 150.0,
        "temperatureC": 27.0,
        "dissolvedOxygenMgL": 2.6,  # Critically low DO
        "pH": 7.4,
        "ammoniaMgL": 0.05,
        "nitrateMgL": 22.0,
        "turbidityNtu": 14.0,
        "salinityPpt": 0.5,
        "previousFeedKg": 5.0,
        "recentAverageFeedKg": 5.2,
        "feedingFrequency": 2,
        "feedQualityScore": 82.0,
        "rainfallMm": 8.0,
        "humidityPercent": 66.0,
        "airTemperatureC": 25.5,
    })


@pytest.fixture
def high_ammonia_input():
    """Scenario 3: Elevated toxic ammonia."""
    return FeedingPredictionInput.from_flat_dict({
        "pond_id": "test_high_ammonia",
        "fishSpecies": "Tilapia",
        "growthStage": "Grow-out",
        "fishAgeDays": 190,
        "biomassKg": 250.0,
        "averageFishWeightG": 150.0,
        "temperatureC": 27.0,
        "dissolvedOxygenMgL": 5.8,
        "pH": 7.8,
        "ammoniaMgL": 0.12,  # Critical ammonia toxicity
        "nitrateMgL": 45.0,
        "turbidityNtu": 18.0,
        "salinityPpt": 0.5,
        "previousFeedKg": 5.0,
        "recentAverageFeedKg": 5.2,
        "feedingFrequency": 2,
        "feedQualityScore": 82.0,
        "rainfallMm": 8.0,
        "humidityPercent": 66.0,
        "airTemperatureC": 25.5,
    })


@pytest.fixture
def high_turbidity_input():
    """Scenario 4: High suspended solids and turbidity."""
    return FeedingPredictionInput.from_flat_dict({
        "pond_id": "test_high_turbidity",
        "fishSpecies": "Tilapia",
        "growthStage": "Grow-out",
        "fishAgeDays": 190,
        "biomassKg": 250.0,
        "averageFishWeightG": 150.0,
        "temperatureC": 27.0,
        "dissolvedOxygenMgL": 5.5,
        "pH": 7.4,
        "ammoniaMgL": 0.03,
        "nitrateMgL": 30.0,
        "turbidityNtu": 65.0,  # High turbidity
        "salinityPpt": 0.5,
        "previousFeedKg": 5.0,
        "recentAverageFeedKg": 5.2,
        "feedingFrequency": 2,
        "feedQualityScore": 82.0,
        "rainfallMm": 75.0,
        "humidityPercent": 80.0,
        "airTemperatureC": 25.5,
    })


@pytest.fixture
def different_fish_age_input():
    """Scenario 5: Advanced age adult fish."""
    return FeedingPredictionInput.from_flat_dict({
        "pond_id": "test_fish_age",
        "fishSpecies": "Tilapia",
        "growthStage": "Adult",
        "fishAgeDays": 650,  # Mature adult age
        "biomassKg": 250.0,
        "averageFishWeightG": 650.0,
        "temperatureC": 27.0,
        "dissolvedOxygenMgL": 6.2,
        "pH": 7.4,
        "ammoniaMgL": 0.025,
        "nitrateMgL": 22.0,
        "turbidityNtu": 14.0,
        "salinityPpt": 0.5,
        "previousFeedKg": 4.0,
        "recentAverageFeedKg": 4.1,
        "feedingFrequency": 2,
        "feedQualityScore": 82.0,
        "rainfallMm": 8.0,
        "humidityPercent": 66.0,
        "airTemperatureC": 25.5,
    })


@pytest.fixture
def different_biomass_input():
    """Scenario 6: High stocked biomass."""
    return FeedingPredictionInput.from_flat_dict({
        "pond_id": "test_high_biomass",
        "fishSpecies": "Tilapia",
        "growthStage": "Adult",
        "fishAgeDays": 350,
        "biomassKg": 850.0,  # High biomass
        "averageFishWeightG": 700.0,
        "temperatureC": 27.0,
        "dissolvedOxygenMgL": 6.5,
        "pH": 7.4,
        "ammoniaMgL": 0.025,
        "nitrateMgL": 22.0,
        "turbidityNtu": 14.0,
        "salinityPpt": 0.5,
        "previousFeedKg": 11.0,
        "recentAverageFeedKg": 11.2,
        "feedingFrequency": 3,
        "feedQualityScore": 85.0,
        "rainfallMm": 8.0,
        "humidityPercent": 66.0,
        "airTemperatureC": 25.5,
    })
