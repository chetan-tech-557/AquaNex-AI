# AquaNex AI — AI-Driven Adaptive Aquaculture Feeding Optimization

**Aarambh WCE Hackathon 2026**

AquaNex AI is a production-grade machine learning and operations research platform that optimizes aquaculture feeding rations, minimizes feed waste, prevents pond water pollution, and provides real-time Explainable AI (SHAP) attributions.

---

## 🌟 Key Highlights

- **Full-Stack Integrated Architecture**: Modern Next.js 16 (React 19, TypeScript, Tailwind CSS) UI connected via REST API to a Python FastAPI backend.
- **Python Backend as Source of Truth**: Production ML models, SciPy constrained optimization, multi-parameter pollution risk calculations, and TreeSHAP explainability drive the UI recommendations.
- **Trained on 293,968 Aquaculture Records**: Real datasets across 200 distinct ponds validated with leak-free `GroupShuffleSplit` on `pond_id`:
  - **Feed Model (Random Forest)**: $R^2 = 0.9991$, $\text{RMSE} = 0.8978$ kg/day, $\text{MAE} = 0.4337$ kg/day (vs static chart baseline $R^2 = 0.8660$).
  - **Waste Model (HistGradientBoosting)**: $R^2 = 0.9616$, $\text{RMSE} = 1.2481\%$, $\text{MAE} = 0.9676\%$.
  - **Pollution Risk Model (HistGradientBoosting)**: $R^2 = 0.9427$, $\text{RMSE} = 3.5678$, $\text{MAE} = 2.8158$ (0–100 score).
- **SciPy Constrained Optimization**: Solves bounded loss minimization across daily meal frequencies ($1 - 4$ meals/day) balancing feed expense against waste penalties and pollution risks.
- **Explainable AI (SHAP)**: Real-time TreeSHAP feature attribution explaining model drivers for each pond prediction displayed directly on the dashboard.
- **SQLite Database**: Persistent parameterized storage for ponds, water readings, feeding history, and recommendations.
- **Robust Test Suite**: 33 passing automated unit, integration, scenario, and model inference tests.

---

## 🚀 Quick Start

### 1. Backend Setup & Automated Test Suite
```bash
# Install Python dependencies
pip install -r requirements.txt

# (Optional) Retrain all 3 ML models from scratch on aquaculture datasets
python backend/scripts/train_models.py

# Run complete pytest suite (all 33 unit, integration, scenario & model tests)
python -m pytest backend/tests -v

# Start FastAPI backend server (port 8000)
python -m uvicorn backend.app.server:app --host 127.0.0.1 --port 8000 --reload
```
Interactive Swagger API documentation is available at `http://localhost:8000/docs`.

### 2. Frontend Setup & Launch
```bash
# Navigate to frontend
cd frontend

# Install dependencies (if not already installed)
npm install

# Start Next.js development server (port 3000)
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser. The frontend automatically connects to `http://localhost:8000` via `NEXT_PUBLIC_API_URL`.

---

## 📂 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── config/          # Domain constants, species profiles, and settings
│   │   ├── schemas/         # Pydantic v2 data models & validation
│   │   ├── data/            # Preprocessing, feature engineering, and physical validation
│   │   ├── models/          # Model loaders and inference wrappers
│   │   ├── prediction/      # Feed, waste, and pollution prediction services
│   │   ├── risk/            # Waste risk and multi-parameter pollution engine
│   │   ├── optimization/    # SciPy objective, constraints, and feeding optimizer
│   │   ├── explainability/  # SHAP TreeExplainer feature attribution
│   │   ├── database/        # SQLite connection, schema, and repository
│   │   ├── services/        # Central recommendation orchestrator
│   │   ├── server.py        # FastAPI server & route handlers
│   │   └── main.py          # Backend entry point
│   ├── trained_models/      # Serialized joblib pipelines, models & metadata JSONs
│   ├── scripts/
│   │   └── train_models.py  # Unified group-aware ML training & evaluation suite
│   ├── tests/               # Pytest suite (33 unit, integration, scenario & ML tests)
│   └── README.md            # In-depth technical backend documentation
├── frontend/                # Next.js 16 (React 19 + TypeScript + Tailwind CSS)
│   ├── app/                 # App router pages & layouts
│   ├── components/          # Dashboard, Optimizer, History & Scenario UI
│   └── lib/                 # Backend API client & domain models
├── ml_feed_optimization.csv # Aquaculture feed dataset (293,968 rows, 200 ponds)
├── ml_waste_prediction.csv  # Feed waste dataset (293,968 rows, 200 ponds)
├── ml_pollution_risk.csv    # Water pollution risk dataset (293,968 rows, 200 ponds)
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