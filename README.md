# AquaNex AI — AI-Driven Adaptive Aquaculture Feeding Optimization

**Aarambh WCE Hackathon 2026**

AquaNex AI is a production-grade machine learning and operations research platform that optimizes aquaculture feeding rations, minimizes feed waste, prevents pond water pollution, and provides real-time Explainable AI (SHAP) attributions.

---

## 🌟 Key Highlights

- **Python-First Modular Architecture**: Production backend adhering to strict separation of concerns (Schemas, Data, Models, Risk, Optimization, Explainability, Database, Services).
- **ML Feeding & Waste Pipelines**: Trained Gradient Boosting & Random Forest models with held-out validation ($R^2 = 0.9617$, $\text{RMSE} = 0.9299$ kg).
- **SciPy Constrained Optimization**: Solves bounded loss minimization across daily meal frequencies ($1 - 4$ meals/day) balancing feed expense against waste penalties and pollution risks.
- **Explainable AI (SHAP)**: Real-time TreeSHAP feature attribution explaining model drivers for each pond prediction.
- **SQLite Database**: Persistent parameterized storage for ponds, water readings, feeding history, and recommendations.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Test Suite (All 24 Tests)
```bash
python -m pytest backend/tests -v
```

### 3. Run Backend Verification
```bash
python backend/app/main.py
```

---

## 📂 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── config/          # Domain constants, species profiles, and settings
│   │   ├── schemas/         # Pydantic v2 data models & validation
│   │   ├── data/            # Preprocessing, feature engineering, and physical validation
│   │   ├── models/          # Model loader and inference wrappers
│   │   ├── prediction/      # Feed, waste, and pollution prediction services
│   │   ├── risk/            # Waste risk and multi-parameter pollution engine
│   │   ├── optimization/    # SciPy objective, constraints, and feeding optimizer
│   │   ├── explainability/  # SHAP TreeExplainer feature attribution
│   │   ├── database/        # SQLite connection, schema, and repository
│   │   ├── services/        # Central recommendation orchestrator
│   │   └── main.py          # Backend entry point
│   ├── data/
│   │   ├── raw/             # Simulation dataset (CSV & JSON)
│   │   └── processed/
│   ├── trained_models/      # Joblib serialized models, pipelines, and metrics
│   ├── scripts/             # Offline training scripts
│   ├── tests/               # Pytest suite (24 unit, integration & scenario tests)
│   └── README.md            # In-depth technical documentation
├── requirements.txt         # Pinned project dependencies
└── README.md
```

---

## 🧪 Tested Demonstration Scenarios

AquaNex AI includes automated test fixtures and dashboard presets for all 6 required Hackathon scenarios:
1. **Scenario 1 — Normal Pond**: Optimal DO, temperature, and feeding; low pollution and waste risk.
2. **Scenario 2 — Low Dissolved Oxygen**: Severe hypoxia detected; biological appetite guard curtails feed ration to protect fish welfare.
3. **Scenario 3 — High Ammonia Toxicity**: Toxic ammonia alert triggered; pollution risk elevated to HIGH with emergency mitigation advice.
4. **Scenario 4 — High Turbidity**: Elevated suspended sediment and runoff; diagnostics recommend aeration and filtration check.
5. **Scenario 5 — Mature Adult Fish**: Life-stage adaptation adjusting maintenance feeding rates.
6. **Scenario 6 — High Biomass**: Dynamic scaling of daily rations according to population density and biomass capacity.

---

## 📜 Scientific Honesty & Disclosures

All training, validation, and demo rows are controlled simulation data generated for the Aarambh WCE Hackathon 2026 prototype. They are not commercial farm sensor measurements. Real-world deployment requires farm-specific sensor calibration and aquaculture specialist supervision.