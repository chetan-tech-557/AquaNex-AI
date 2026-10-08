"""Input schemas and validation rules for AquaNex AI.

Validates fish stock, water quality, feeding history, and contextual weather data.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, model_validator
from backend.app.config.constants import SUPPORTED_SPECIES, SUPPORTED_GROWTH_STAGES


class FishInfo(BaseModel):
    """Biological and demographic information regarding the stocked population."""

    species: str = Field(
        default="Tilapia",
        description="Cultured finfish species name (e.g., Tilapia, Carp, Salmon)",
    )
    fish_age_days: int = Field(
        default=190,
        ge=1,
        le=2000,
        description="Age of fish in days since hatching",
    )
    growth_stage: str = Field(
        default="Grow-out",
        description="Life stage: Fry, Juvenile, Grow-out, Adult",
    )
    biomass_kg: float = Field(
        default=250.0,
        gt=0.0,
        le=50000.0,
        description="Total living fish biomass in the pond (kg)",
    )
    average_fish_weight_g: float = Field(
        default=150.0,
        gt=0.0,
        le=15000.0,
        description="Mean weight of an individual fish in grams",
    )
    fish_count: Optional[int] = Field(
        default=None,
        ge=1,
        description="Estimated population count. Auto-computed from biomass and avg weight if omitted.",
    )

    @model_validator(mode="after")
    def compute_and_validate_population(self) -> "FishInfo":
        if self.species not in SUPPORTED_SPECIES:
            # We allow case-insensitive match or fall back gracefully
            matched = [s for s in SUPPORTED_SPECIES if s.lower() == self.species.lower()]
            if matched:
                self.species = matched[0]
            else:
                raise ValueError(
                    f"Species '{self.species}' is not supported. Supported species: {SUPPORTED_SPECIES}"
                )

        if self.growth_stage not in SUPPORTED_GROWTH_STAGES:
            matched_stage = [s for s in SUPPORTED_GROWTH_STAGES if s.lower() == self.growth_stage.lower()]
            if matched_stage:
                self.growth_stage = matched_stage[0]
            else:
                raise ValueError(
                    f"Growth stage '{self.growth_stage}' is not supported. Supported stages: {SUPPORTED_GROWTH_STAGES}"
                )

        if self.fish_count is None:
            # Auto-calculate: biomass_kg * 1000 / avg_weight_g
            self.fish_count = max(1, int(round((self.biomass_kg * 1000.0) / self.average_fish_weight_g)))

        return self


class WaterQuality(BaseModel):
    """Physicochemical pond water quality parameters."""

    water_temperature_c: float = Field(
        default=27.0,
        ge=4.0,
        le=42.0,
        description="Water temperature in degrees Celsius",
    )
    dissolved_oxygen_mg_l: float = Field(
        default=6.2,
        ge=0.1,
        le=20.0,
        description="Dissolved oxygen concentration in mg/L (ppm)",
    )
    ph: float = Field(
        default=7.4,
        ge=4.5,
        le=10.5,
        description="Water pH measure (acidity / alkalinity)",
    )
    ammonia_mg_l: float = Field(
        default=0.025,
        ge=0.0,
        le=2.0,
        description="Total ammonia nitrogen concentration in mg/L",
    )
    nitrate_mg_l: float = Field(
        default=22.0,
        ge=0.0,
        le=300.0,
        description="Nitrate concentration in mg/L",
    )
    turbidity: float = Field(
        default=14.0,
        ge=0.0,
        le=250.0,
        description="Turbidity measurement in Nephelometric Turbidity Units (NTU)",
    )
    salinity_ppt: float = Field(
        default=0.5,
        ge=0.0,
        le=45.0,
        description="Salinity in parts per thousand (ppt)",
    )


class FeedingInfo(BaseModel):
    """Historical and operational feeding metrics."""

    feed_quality_score: float = Field(
        default=82.0,
        ge=10.0,
        le=100.0,
        description="Estimated feed nutritional & pellet integrity index (0-100)",
    )
    previous_feed_kg: float = Field(
        default=5.0,
        ge=0.0,
        le=1000.0,
        description="Feed quantity delivered on the previous day (kg)",
    )
    recent_average_feed_kg: float = Field(
        default=5.2,
        ge=0.0,
        le=1000.0,
        description="Rolling 3-7 day average daily feed quantity (kg)",
    )
    feeding_frequency: int = Field(
        default=2,
        ge=1,
        le=6,
        description="Number of feeding meals distributed per day",
    )


class EnvironmentalInfo(BaseModel):
    """Contextual ambient environmental and weather conditions."""

    rainfall_mm: float = Field(
        default=8.0,
        ge=0.0,
        le=500.0,
        description="Daily precipitation in mm",
    )
    humidity_percent: float = Field(
        default=66.0,
        ge=5.0,
        le=100.0,
        description="Relative ambient humidity percentage",
    )
    air_temperature_c: float = Field(
        default=25.5,
        ge=-5.0,
        le=55.0,
        description="Ambient air temperature in degrees Celsius",
    )


class FeedingPredictionInput(BaseModel):
    """Unified feeding prediction input model.

    Supports structured sub-models as well as flat keyword arguments for convenience.
    """

    pond_id: Optional[str] = Field(default="pond_01", description="Identifier for target aquaculture pond")
    fish: FishInfo = Field(default_factory=FishInfo)
    water: WaterQuality = Field(default_factory=WaterQuality)
    feeding: FeedingInfo = Field(default_factory=FeedingInfo)
    environment: EnvironmentalInfo = Field(default_factory=EnvironmentalInfo)

    @classmethod
    def from_flat_dict(cls, data: Dict[str, Any]) -> "FeedingPredictionInput":
        """Construct from flat dictionary matching either prototype camelCase or snake_case."""
        # Normalize keys
        def get_val(keys: list, default):
            for k in keys:
                if k in data and data[k] is not None:
                    return data[k]
            return default

        fish = FishInfo(
            species=str(get_val(["species", "fishSpecies", "fish_species"], "Tilapia")),
            fish_age_days=int(get_val(["fish_age_days", "fishAgeDays", "age_days"], 190)),
            growth_stage=str(get_val(["growth_stage", "growthStage"], "Grow-out")),
            biomass_kg=float(get_val(["biomass_kg", "biomassKg", "biomass"], 250.0)),
            average_fish_weight_g=float(get_val(["average_fish_weight_g", "averageFishWeightG", "fish_weight_g"], 150.0)),
            fish_count=get_val(["fish_count", "fishCount"], None),
        )

        water = WaterQuality(
            water_temperature_c=float(get_val(["water_temperature_c", "temperatureC", "water_temp"], 27.0)),
            dissolved_oxygen_mg_l=float(get_val(["dissolved_oxygen_mg_l", "dissolvedOxygenMgL", "do_mg_l"], 6.2)),
            ph=float(get_val(["ph", "pH"], 7.4)),
            ammonia_mg_l=float(get_val(["ammonia_mg_l", "ammoniaMgL", "ammonia"], 0.025)),
            nitrate_mg_l=float(get_val(["nitrate_mg_l", "nitrateMgL", "nitrate"], 22.0)),
            turbidity=float(get_val(["turbidity", "turbidityNtu", "turbidity_ntu"], 14.0)),
            salinity_ppt=float(get_val(["salinity_ppt", "salinityPpt", "salinity"], 0.5)),
        )

        feeding = FeedingInfo(
            feed_quality_score=float(get_val(["feed_quality_score", "feedQualityScore"], 82.0)),
            previous_feed_kg=float(get_val(["previous_feed_kg", "previousFeedKg"], 5.0)),
            recent_average_feed_kg=float(get_val(["recent_average_feed_kg", "recentAverageFeedKg", "recent_feed_history"], 5.2)),
            feeding_frequency=int(get_val(["feeding_frequency", "feedingFrequency"], 2)),
        )

        environment = EnvironmentalInfo(
            rainfall_mm=float(get_val(["rainfall_mm", "rainfallMm"], 8.0)),
            humidity_percent=float(get_val(["humidity_percent", "humidityPercent"], 66.0)),
            air_temperature_c=float(get_val(["air_temperature_c", "airTemperatureC"], 25.5)),
        )

        pond_id = str(get_val(["pond_id", "pondId"], "pond_01"))

        return cls(pond_id=pond_id, fish=fish, water=water, feeding=feeding, environment=environment)
