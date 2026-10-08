"""Tests for input validation and physical plausibility guards."""

import pytest
from pydantic import ValidationError as PydanticValidationError
from backend.app.schemas.input_schema import FeedingPredictionInput, FishInfo
from backend.app.data.validation import validate_input_data, ValidationError


def test_valid_input_passes(normal_pond_input):
    is_valid, errors, warnings = validate_input_data(normal_pond_input)
    assert is_valid is True
    assert len(errors) == 0


def test_negative_biomass_rejected():
    with pytest.raises((PydanticValidationError, ValueError)):
        FishInfo(biomass_kg=-50.0, average_fish_weight_g=100.0)


def test_zero_fish_weight_rejected():
    with pytest.raises((PydanticValidationError, ValueError)):
        FishInfo(biomass_kg=200.0, average_fish_weight_g=0.0)


def test_unsupported_species_rejected():
    with pytest.raises((PydanticValidationError, ValueError)):
        FishInfo(species="Piranha", biomass_kg=200.0, average_fish_weight_g=100.0)


def test_negative_dissolved_oxygen_rejected():
    with pytest.raises((PydanticValidationError, ValueError)):
        FeedingPredictionInput.from_flat_dict({
            "dissolvedOxygenMgL": -1.5
        })


def test_implausible_ph_rejected():
    with pytest.raises((PydanticValidationError, ValueError)):
        FeedingPredictionInput.from_flat_dict({
            "pH": 14.5
        })


def test_biological_warning_on_low_do():
    inp = FeedingPredictionInput.from_flat_dict({
        "species": "Tilapia",
        "dissolvedOxygenMgL": 2.5
    })
    is_valid, errors, warnings = validate_input_data(inp)
    assert is_valid is True
    assert any("survival threshold" in w or "Dissolved oxygen" in w for w in warnings)


def test_auto_fish_count_calculation():
    fish = FishInfo(biomass_kg=100.0, average_fish_weight_g=200.0)
    # 100 kg * 1000 g/kg / 200 g/fish = 500 fish
    assert fish.fish_count == 500
