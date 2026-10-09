AquaNexsus cleaned feature pack

The provided 300K dataset was cleaned and split by the features needed by the
AquaNexsus website and ML pipeline.

Cleaning performed:
- duplicate record removal
- malformed/parse validation
- removal of rows flagged with label_quality_flag != OK
- broad domain/range validation
- feed_consumed_g capped at feed_given_g
- feed_waste_g recalculated as feed_given_g - feed_consumed_g
- biomass_kg recalculated as fish_count * avg_weight_g / 1000
- derived time, season, temperature-deviation, feeding-efficiency and water-alert features

Files:
- cleaned_master_ml_ready.csv
- features_water_quality.csv
- features_fish_growth.csv
- features_feeding.csv
- features_environment.csv
- features_feed_info.csv
- ml_feed_optimization.csv
- ml_waste_prediction.csv
- ml_pollution_risk.csv
- website_pond_snapshot.csv
- excluded_rows.csv
- CLEANING_REPORT.csv
- FEATURE_MAP_FOR_WEBSITE.csv

Model targets:
Feed optimization -> recommended_feed_g
Waste prediction -> expected_waste_pct
Pollution risk -> pollution_risk_score / pollution_risk_level

Important:
These source rows are synthetic prototype data. Cleaning does not turn them into
real-world measurements. Use real farm/sensor data for claims about production accuracy.
