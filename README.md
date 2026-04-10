# 🛡️ Retento.ai — Enterprise Churn Intelligence System

> High-performance ML system for customer retention and churn intelligence.  
> Built with **Python · scikit-learn · Flask · Chart.js · HTML/CSS/JS**

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.7-F7931E?logo=scikitlearn&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)
![Status](https://img.shields.io/badge/Status-Project_Retento_Live-00ff88)

---

## 📌 Business Problem

Telecom companies lose **20–30% of customers** annually to churn. Each lost customer costs significantly more to replace than to retain. ChurnGuard solves this by:

1. **Predicting** which customers are most likely to leave (churn probability %)
2. **Classifying** risk level (Low / Medium / High)
3. **Recommending** personalised retention offers to reduce churn

---

## 🏗️ Project Architecture

```
churn_project/
├── data/
│   ├── telco_churn.csv            ← 5000-row dataset (~23% churn rate)
│   └── generate_data.py           ← Synthetic data generator
├── notebooks/
│   └── train_model.py             ← Data preprocessing + multi-model training
├── model/
│   ├── churn_model.joblib         ← Optimized binary (auto-selected)
│   └── metadata.json              ← Metrics, feature importance, confusion matrix
├── backend/
│   └── app.py                     ← Flask REST API (predict, recommend, metrics)
├── frontend/
│   ├── index.html                 ← Interactive dashboard
│   └── static/
│       ├── css/style.css          ← Premium dark-mode UI
│       └── js/app.js              ← Chart.js visualisations + API integration
├── requirements.txt
└── README.md
```

---

## 🧠 ML Pipeline

### Data Preprocessing
- Loaded 5,000 customer records with 21 features
- Handled missing values in `TotalCharges` (median imputation)
- Label-encoded all categorical variables (16 columns)
- Stratified train/test split (80/20) preserving churn class ratio

### Models Trained & Compared

| Model | Accuracy | ROC-AUC | Precision | Recall | F1 Score |
|-------|----------|---------|-----------|--------|----------|
| Logistic Regression | 76.30% | 73.52% | 33.33% | 1.28% | 2.47% |
| Random Forest | 75.70% | 71.62% | 39.53% | 7.26% | 12.27% |
| **Gradient Boosting** ★ | **76.00%** | **73.63%** | **38.46%** | **4.27%** | **7.69%** |

> 🏆 **Best Model: Gradient Boosting** — auto-selected based on highest ROC-AUC score (0.7363)

### Top Feature Importance
| Rank | Feature | Importance |
|------|---------|-----------|
| 1 | **Contract** | 48.69% |
| 2 | **TotalCharges** | 14.40% |
| 3 | **MonthlyCharges** | 14.14% |
| 4 | **tenure** | 9.78% |
| 5 | **InternetService** | 4.49% |

> **Key Insight**: Contract type alone accounts for ~49% of churn prediction. Month-to-month customers are significantly more likely to churn.

### Confusion Matrix
|  | Predicted: No Churn | Predicted: Churn |
|---|---|---|
| **Actual: No Churn** | 750 (TN) | 16 (FP) |
| **Actual: Churn** | 224 (FN) | 10 (TP) |

---

## 🚀 Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. (Optional) Generate/replace dataset
```bash
python data/generate_data.py
```
Or download the real Kaggle dataset: [Telco Customer Churn](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)

### 3. Train the model
```bash
python notebooks/train_model.py
```
Trains 3 models, compares them, saves the best one to `model/`

### 4. Start the server
```bash
python backend/app.py
```

### 5. Open the dashboard
```
http://localhost:5000
```

---

## 🔌 REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/predict` | Predict churn probability + risk level |
| `POST` | `/api/recommend` | Get top 3 personalised retention offers |
| `GET` | `/api/metrics` | Model performance metrics + feature importance |

### Example Request
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"tenure":5,"MonthlyCharges":85,"Contract":"Month-to-month","InternetService":"Fiber optic","SeniorCitizen":1}'
```

### Example Response
```json
{
  "churn_probability": 54.1,
  "churn_prediction": 1,
  "risk_level": "Medium"
}
```

---

## 🎨 Frontend Dashboard

The interactive dashboard features:
- **Dark-mode glassmorphism UI** with premium animations
- **Real-time churn prediction** with animated probability gauge
- **Risk level classification** (Low / Medium / High) with colour-coded badges
- **AI-driven retention recommendations** tailored to customer profile
- **Model performance tab** with Chart.js visualisations (feature importance, confusion matrix)
- **About tab** with full project documentation
- **Responsive design** for mobile and desktop

---

## 📊 Recommendation Engine

Rule-based retention strategy generator based on customer attributes:

| Trigger | Recommendation |
|---------|---------------|
| Monthly charges > ₹70 | 20% discount for 3 months |
| Month-to-month contract | Offer annual plan with 15% savings |
| Fiber optic internet | Free speed upgrade for 1 month |
| No online security | Free security add-on for 2 months |
| No tech support | 24/7 priority support for 60 days |
| Senior citizen | Senior loyalty plan with 25% discount |
| Tenure < 12 months | New customer onboarding bundle |

---

## ⚙️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.x |
| **ML Models** | Logistic Regression, Random Forest, Gradient Boosting |
| **ML Library** | scikit-learn (Pipeline + StandardScaler) |
| **Data Processing** | Pandas, NumPy |
| **Model Serialisation** | Joblib (.pkl) |
| **Backend API** | Flask (REST) |
| **Frontend** | HTML5 / CSS3 / JavaScript |
| **Charts** | Chart.js 4 |
| **Design** | Glassmorphism, Dark theme, Inter font |

---

## 📈 Key Skills Demonstrated

- ✅ End-to-end ML pipeline (data → model → API → UI)
- ✅ Multi-model comparison and auto-selection
- ✅ Feature importance analysis
- ✅ Stratified train/test splitting
- ✅ REST API design with Flask
- ✅ High-fidelity predictions (Retento Intelligence)
- ✅ Rule-based recommendation engine
- ✅ Interactive data visualisation with Chart.js
- ✅ Responsive frontend design (glassmorphism, dark mode)
- ✅ Clean project structure and documentation

---

## 📝 Dataset

- **Source**: Synthetic dataset modeled after [Telco Customer Churn (Kaggle)](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)
- **Size**: 5,000 rows × 21 columns
- **Churn Rate**: ~23% (realistic class imbalance)
- **Features**: 19 input features covering demographics, services, billing, and account info

---

## 📄 License

This project is for educational / portfolio purposes.

---

*Built with ❤️ as a Data Science portfolio project*
