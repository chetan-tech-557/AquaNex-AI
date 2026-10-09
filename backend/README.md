# AquaNex AI — Backend Architecture & Technical Documentation

**Aarambh WCE Hackathon 2026**  
*AI-Driven Adaptive Aquaculture Feeding Optimization*

---

## 1. Architecture Overview

AquaNex AI replaces static, chart-based feeding in aquaculture with an adaptive, multi-stage machine learning and constrained optimization pipeline. The backend is designed in modular, production-style Python with strict separation of concerns:

```
INPUT (Fish Stock, Water Quality, Prior Feed, Weather)
  │
  ▼
[Validation Layer] (Pydantic schemas + Biological plausibility guards)
  │
  ▼
[Feature Engineering & Preprocessing] (AquaNexPreprocessor, domain indicators)
  │
  ▼
[ML Prediction Layer]
  ├── Feed Requirement Model (Gradient Boosting / Random Forest Regressor)
  ├── Feed Waste Model (Empirical / ML Regressor)
  └── Pollution Risk Model & Calibrator
  │
  ▼
[Risk Analysis Engines]
  ├── Feed Waste Risk Classifier (LOW / MEDIUM / HIGH)
  └── Multi-Parameter Pond Water Pollution Engine (DO, Ammonia, Turbidity, Waste)
  │
  ▼
[SciPy Optimization Engine] (Constrained Loss Minimization across Meal Frequencies)
  │
  ▼
[Explainable AI Layer] (TreeSHAP feature attributions & diagnostic summary)
  │
  ▼
[SQLite Storage] (Parameterized historical tracking & audit logs)
  │
  ▼
FINAL RECOMMENDATION RESPONSE OBJECT
```

---

## 2. Pipeline Data Flow

1. **Input Normalization**: Incoming flat dictionaries or nested objects are validated against `FeedingPredictionInput` (Pydantic v2).
2. **Sanity & Biological Checks**: Ensures non-negative biomass, physical ranges for pH ($3.0 - 11.0$), DO, temperature, and feeding records.
3. **Feature Derivation**: Computes derived ratios such as `feed_to_biomass_ratio`, `temperature_deviation` from species optimal temperature, and `do_stress_indicator`.
4. **Appetite Estimation**: Predicts daily feed demand in kilograms using the champion Gradient Boosting model with an adverse-condition hypoxia guard.
5. **Waste & Pollution Modeling**: Evaluates unconsumed pellet degradation and pond biochemical oxygen demand (BOD).
6. **SciPy Constrained Optimization**: Solves for optimal total daily feed and meal frequency ($1 - 4$ meals/day) minimizing feed expense, waste penalties, and pollution risk.
7. **TreeSHAP Attribution**: Computes exact Shapley values to explain which pond factors increased or reduced the feeding recommendation.
8. **Persistence**: Saves recommendations, water metrics, and schedules into SQLite (`aquanex.db`).

---

## 3. Input Data Schema

### Fish Information
- `species`: Cultured fish species (`Tilapia`, `Carp`, `Salmon`)
- `fish_age_days`: Population age in days ($1 - 2000$)
- `growth_stage`: Life stage (`Fry`, `Juvenile`, `Grow-out`, `Adult`)
- `biomass_kg`: Total stocked biomass in kg ($> 0$)
- `average_fish_weight_g`: Mean individual weight in grams ($> 0$)
- `fish_count`: Population count (auto-computed if omitted: $\frac{\text{biomass\_kg} \times 1000}{\text{average\_fish\_weight\_g}}$)

### Water Quality Information
- `water_temperature_c`: Water temperature in Celsius ($4.0 - 42.0^\circ\text{C}$)
- `dissolved_oxygen_mg_l`: Dissolved oxygen concentration ($0.1 - 20.0$ mg/L)
- `ph`: Water pH ($4.5 - 10.5$)
- `ammonia_mg_l`: Total ammonia nitrogen ($0.0 - 2.0$ mg/L)
- `nitrate_mg_l`: Nitrate concentration ($0.0 - 300.0$ mg/L)
- `turbidity`: Suspended solids measure in NTU ($0.0 - 250.0$)
- `salinity_ppt`: Salinity in parts per thousand ($0.0 - 45.0$)

### Feeding Operations
- `previous_feed_kg`: Feeding quantity fed yesterday (kg)
- `recent_average_feed_kg`: Rolling 3-7 day daily average feed (kg)
- `feeding_frequency`: Number of meals administered per day ($1 - 6$)
- `feed_quality_score`: Feed integrity index ($10 - 100$)

### Contextual Environment
- `rainfall_mm`: Daily precipitation ($0.0 - 500.0$ mm)
- `humidity_percent`: Relative air humidity ($5\% - 100\%$)
- `air_temperature_c`: Ambient air temperature ($-5.0 - 55.0^\circ\text{C}$)

---

## 4. Feature Engineering

Domain-informed features implemented in `backend/app/data/feature_engineering.py`:

| Feature | Mathematical Definition | Domain Rationale |
|---|---|---|
| `feed_to_biomass_ratio` | $\frac{\text{previous\_feed\_kg}}{\text{biomass\_kg}}$ | Prior-day feeding intensity |
| `biomass_per_fish` | $\frac{\text{biomass\_kg}}{\text{fish\_count}}$ | Fish stocking density / average fish mass |
| `temperature_deviation` | $\|T_{\text{water}} - T_{\text{optimal}}\|$ | Species-specific thermal metabolic deviation |
| `do_stress_indicator` | $\max(0, \text{DO}_{\text{min}} - \text{DO})$ | Respiratory limitation on appetite |
| `ammonia_stress_indicator` | $\max(0, \text{Ammonia} - \text{Ammonia}_{\text{safe}})$ | Excretion and branchial stress |
| `recent_feeding_trend` | $\text{Feed}_{\text{prev}} - \text{Feed}_{\text{avg}}$ | Feeding surge or appetite drop signal |
| `feed_quality_factor` | $\frac{\text{FeedQualityScore}}{100.0}$ | Nutritional efficiency and pellet stability |

---

## 5. Machine Learning Models & Training Pipeline

### Candidate Comparison & Selection
Trained on 293,968 aquaculture records across 200 distinct ponds using a strict group-aware split (`GroupShuffleSplit` on `pond_id`: 160 training ponds / 40 test ponds; 235,098 train rows / 58,870 test rows) preventing intra-pond data leakage.

#### Model A: Feed Requirement Regressor (Target: `recommended_feed_g`, evaluated in kg/day)
| Candidate Model | Test MAE (kg) | Test RMSE (kg) | Test $R^2$ | Status |
|---|---|---|---|---|
| **Random Forest Regressor (n=40, depth=14)** | **0.4337 kg** | **0.8978 kg** | **0.9991** | **Champion Selected** |
| HistGradientBoostingRegressor | 0.4429 kg | 0.9060 kg | 0.9990 | Candidate Evaluated |
| GradientBoostingRegressor (subsample=0.5) | 0.5186 kg | 1.0543 kg | 0.9987 | Candidate Evaluated |
| Static Feeding Chart Baseline (Species/Biomass) | 8.8710 kg | 10.3546 kg | 0.8660 | Domain Reference |
| Naive Mean Baseline | 23.3601 kg | 28.2562 kg | -0.0001 | Naive Reference |

#### Model B: Feed Waste Regressor (Target: `expected_waste_pct` in %)
| Candidate Model | Test MAE (%) | Test RMSE (%) | Test $R^2$ | Status |
|---|---|---|---|---|
| **HistGradientBoostingRegressor** | **0.9676%** | **1.2481%** | **0.9616** | **Champion Selected** |
| RandomForestRegressor (n=30, depth=12) | 1.0118% | 1.3090% | 0.9578 | Candidate Evaluated |
| Naive Mean Baseline | 6.0125% | 6.3980% | -0.0084 | Naive Reference |

#### Model C: Pond Pollution Risk Regressor (Target: `pollution_risk_score` 0–100)
| Candidate Model | Test MAE | Test RMSE | Test $R^2$ | Status |
|---|---|---|---|---|
| **HistGradientBoostingRegressor** | **2.8158** | **3.5678** | **0.9427** | **Champion Selected** |
| RandomForestRegressor (n=30, depth=12) | 2.9234 | 3.6920 | 0.9386 | Candidate Evaluated |
| Naive Mean Baseline | 12.3104 | 14.8966 | -0.0041 | Naive Reference |

### Training Script
All three models, pipelines, and evaluation metrics are trained and exported via:
```bash
python backend/scripts/train_models.py
```
Outputs saved to `backend/trained_models/`:
- `feed_model.joblib`, `feed_pipeline.joblib`, `feed_model_metadata.json`
- `waste_model.joblib`, `waste_pipeline.joblib`, `waste_model_metadata.json`
- `pollution_model.joblib`, `pollution_pipeline.joblib`, `pollution_model_metadata.json`
- `model_metrics.json`

---

## 6. Risk Methodology

### Feed Waste Risk
Calculated from expected uneaten feed, temperature deviation, low DO, and feed quality index:
- **LOW** ($0 - 29$): Normal feeding efficiency; minimal waste.
- **MEDIUM** ($30 - 64$): Moderate thermal deviation or minor overfeeding.
- **HIGH** ($65 - 100$): Severe hypoxia, low pellet stability, or feeding in toxic water.

### Multi-Parameter Pond Water Pollution Engine
Combines 6 weighted parameters with emergency overrides:
1. **Dissolved Oxygen Stress** (Weight: 25%)
2. **Ammonia Toxicity** (Weight: 30%)
3. **Turbidity / Suspended Solids** (Weight: 15%)
4. **Nitrate Buildup** (Weight: 10%)
5. **pH Aberration** (Weight: 10%)
6. **Decaying Feed Waste Burden** (Weight: 10%)

Emergency rule: If Ammonia $\ge 0.08$ mg/L or $\text{DO} < 3.0$ mg/L, risk score floor is clamped to $\ge 85$ (HIGH).

---

## 7. SciPy Optimization Formulation

### Objective Function
$$\min_{F, M} \left[ C_{\text{feed}} \cdot F + C_{\text{waste}} \cdot W(F, M) + \lambda_{\text{poll}} \cdot P(F) + \mu_{\text{meal}} \cdot (M - 1) \right]$$

Where:
- $F$: Daily feed ration (kg)
- $M$: Number of meals per day ($1, 2, 3, 4$)
- $C_{\text{feed}} = \$2.00$/kg (feed cost)
- $C_{\text{waste}} = \$12.00$/kg (penalty for unconsumed rotten pellets)
- $\lambda_{\text{poll}} = 0.15$ (pollution risk penalty weight)
- $\mu_{\text{meal}} = \$0.10$ (operational feeder wear penalty)
- $W(F, M) = W_0 \cdot \left(\frac{F}{F_{\text{appetite}}}\right)^{1.8} \cdot \left(\frac{2}{M}\right)^{0.4}$

### Constraints
- $F_{\min} \ge \max(0.1, 0.70 \cdot F_{\text{appetite}})$
- $F_{\max} \le \min(1.25 \cdot F_{\text{appetite}}, 0.08 \cdot \text{biomass\_kg})$
- **Hypoxia Emergency Bound**: When $\text{DO} < 3.0$ mg/L, $F_{\max} \le 0.50 \cdot F_{\text{appetite}}$

---

## 8. Explainable AI (SHAP)

Uses `shap.TreeExplainer` on the fitted tree ensemble:
- Quantifies exact feature impact ($\pm\text{kg}$) on recommended ration.
- Labels impact direction (`INCREASES FEED` vs `DECREASES FEED`).
- Displays ranked factors without making unwarranted claims of physiological causation.

---

## 9. SQLite Database Schema

Located at `backend/aquanex.db`:
- `ponds`: `(pond_id, name, volume_m3, location, created_at)`
- `fish_stocks`: `(id, pond_id, species, growth_stage, fish_age_days, fish_count, biomass_kg, average_fish_weight_g, recorded_at)`
- `water_measurements`: `(id, pond_id, water_temperature_c, dissolved_oxygen_mg_l, ph, ammonia_mg_l, nitrate_mg_l, turbidity, salinity_ppt, recorded_at)`
- `feeding_logs`: `(id, pond_id, feed_quantity_kg, meal_count, feed_quality_score, recorded_at)`
- `recommendations`: `(id, pond_id, recommended_feed_kg, optimized_feed_kg, expected_waste_kg, waste_risk_score, waste_risk_level, pollution_risk_score, pollution_risk_level, number_of_meals, meal_schedule_json, explanation_summary, baseline_feed_kg, cost_saved_usd, recorded_at)`

---

## 10. How to Run & Test

### Run Automated Test Suite
```bash
python -m pytest backend/tests -v
```
All 33 unit, integration, scenario, and model inference tests execute and pass in ~4.9 seconds.

### Retrain Models (Offline Pipeline)
```bash
python backend/scripts/train_models.py
```
This executes the unified group-aware training pipeline on 293,968 rows across 200 ponds without data leakage and exports model pipelines and metadata.

### Run Backend Server
```bash
python -m uvicorn backend.app.server:app --host 127.0.0.1 --port 8000 --reload
```
Interactive OpenAPI / Swagger docs are available at `http://127.0.0.1:8000/docs`.

### Run Backend Verification Script
```bash
python backend/app/main.py
```

---

## 11. Scientific Disclosures & Prototype Limitations
1. **Simulation Data**: Dataset comprises controlled mathematical simulations calibrated for the Aarambh WCE Hackathon 2026.
2. **Species Boundary**: Current model profiles are optimized for Tilapia, Carp, and Salmon.
3. **Sensor Calibration**: Real-world farm integration requires periodic probe drift calibration and local water hardness corrections.
