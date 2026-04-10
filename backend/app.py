"""
Churn Prediction API - Flask Backend
Endpoints:
  POST /api/predict    - predict churn probability for a customer
  POST /api/recommend  - get retention recommendations
  GET  /api/metrics    - model performance metrics
  GET  /               - serve frontend
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'model', 'churn_model.joblib')
META_PATH = os.path.join(BASE_DIR, 'model', 'metadata.json')
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

app = Flask(__name__, static_folder=os.path.join(FRONTEND_DIR, 'static'))

# Load model and metadata at startup
print("Loading model...")
model = joblib.load(MODEL_PATH)
with open(META_PATH) as f:
    metadata = json.load(f)

FEATURES = metadata['feature_names']

# -------------------------------------------------------------------
# RECOMMENDATION ENGINE
# Rule-based: maps customer profile to retention offers
# -------------------------------------------------------------------

RECOMMENDATIONS = {
    'high_monthly_charges': {
        'title': 'Discount on Monthly Plan',
        'detail': '20% discount for next 3 months to reduce billing pressure.',
        'icon': 'discount',
    },
    'month_to_month': {
        'title': 'Switch to Annual Contract',
        'detail': 'Annual plan saves 15% — lock in low rate and reduce churn risk.',
        'icon': 'contract',
    },
    'fiber_optic': {
        'title': 'Free Speed Upgrade',
        'detail': 'Complimentary 1-month upgrade to premium fiber tier.',
        'icon': 'internet',
    },
    'no_online_security': {
        'title': 'Free Security Add-on',
        'detail': 'Activate Online Security & Backup free for 2 months.',
        'icon': 'security',
    },
    'no_tech_support': {
        'title': 'Priority Tech Support',
        'detail': 'Enroll in 24/7 priority support at no extra charge for 60 days.',
        'icon': 'support',
    },
    'senior_citizen': {
        'title': 'Senior Loyalty Bonus',
        'detail': 'Special senior citizen plan with 25% off and dedicated helpline.',
        'icon': 'loyalty',
    },
    'low_tenure': {
        'title': 'New Customer Loyalty Pack',
        'detail': 'Exclusive onboarding bundle — free device protection + 1 month waiver.',
        'icon': 'loyalty',
    },
    'default': {
        'title': 'Loyalty Reward Points',
        'detail': 'Earn 2x reward points for next 6 months — redeemable on bills.',
        'icon': 'reward',
    },
}


def get_recommendations(raw_input: dict) -> list:
    """Return top 3 personalized recommendations based on customer profile."""
    recs = []

    monthly = float(raw_input.get('MonthlyCharges', 50))
    contract = str(raw_input.get('Contract', ''))
    internet = str(raw_input.get('InternetService', ''))
    security = str(raw_input.get('OnlineSecurity', ''))
    support = str(raw_input.get('TechSupport', ''))
    senior = int(raw_input.get('SeniorCitizen', 0))
    tenure = int(raw_input.get('tenure', 12))

    if monthly > 70:
        recs.append(RECOMMENDATIONS['high_monthly_charges'])
    if 'month' in contract.lower():
        recs.append(RECOMMENDATIONS['month_to_month'])
    if 'fiber' in internet.lower():
        recs.append(RECOMMENDATIONS['fiber_optic'])
    if security in ['No', '0', 0]:
        recs.append(RECOMMENDATIONS['no_online_security'])
    if support in ['No', '0', 0]:
        recs.append(RECOMMENDATIONS['no_tech_support'])
    if senior == 1:
        recs.append(RECOMMENDATIONS['senior_citizen'])
    if tenure < 12:
        recs.append(RECOMMENDATIONS['low_tenure'])

    # Deduplicate and take top 3
    seen = set()
    unique_recs = []
    for r in recs:
        if r['title'] not in seen:
            seen.add(r['title'])
            unique_recs.append(r)
        if len(unique_recs) == 3:
            break

    if len(unique_recs) < 3:
        unique_recs.append(RECOMMENDATIONS['default'])

    return unique_recs[:3]


def encode_input(raw: dict) -> pd.DataFrame:
    """
    Encode raw customer dict (same as training preprocessing).
    Maps string values → numeric exactly as LabelEncoder would.
    """
    MAPS = {
        'gender':          {'Female': 0, 'Male': 1},
        'Partner':         {'No': 0, 'Yes': 1},
        'Dependents':      {'No': 0, 'Yes': 1},
        'PhoneService':    {'No': 0, 'Yes': 1},
        'MultipleLines':   {'No': 0, 'No phone service': 1, 'Yes': 2},
        'InternetService': {'DSL': 0, 'Fiber optic': 1, 'No': 2},
        'OnlineSecurity':  {'No': 0, 'No internet service': 1, 'Yes': 2},
        'OnlineBackup':    {'No': 0, 'No internet service': 1, 'Yes': 2},
        'DeviceProtection':{'No': 0, 'No internet service': 1, 'Yes': 2},
        'TechSupport':     {'No': 0, 'No internet service': 1, 'Yes': 2},
        'StreamingTV':     {'No': 0, 'No internet service': 1, 'Yes': 2},
        'StreamingMovies': {'No': 0, 'No internet service': 1, 'Yes': 2},
        'Contract':        {'Month-to-month': 0, 'One year': 1, 'Two year': 2},
        'PaperlessBilling':{'No': 0, 'Yes': 1},
        'PaymentMethod': {
            'Bank transfer (automatic)': 0,
            'Credit card (automatic)': 1,
            'Electronic check': 2,
            'Mailed check': 3,
        },
    }
    row = {}
    for feat in FEATURES:
        val = raw.get(feat, 0)
        if feat in MAPS:
            row[feat] = MAPS[feat].get(str(val), 0)
        else:
            row[feat] = float(val) if val != '' else 0.0

    return pd.DataFrame([row])[FEATURES]


# -------------------------------------------------------------------
# ROUTES
# -------------------------------------------------------------------

@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'static'), filename)


@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        encoded = encode_input(data)
        prob = float(model.predict_proba(encoded)[0][1])
        prediction = int(model.predict(encoded)[0])

        if prob >= 0.65:
            risk = 'High'
        elif prob >= 0.35:
            risk = 'Medium'
        else:
            risk = 'Low'

        return jsonify({
            'churn_probability': round(prob * 100, 1),
            'churn_prediction': prediction,
            'risk_level': risk,
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/recommend', methods=['POST'])
def recommend():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        recs = get_recommendations(data)
        return jsonify({'recommendations': recs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/metrics', methods=['GET'])
def metrics():
    return jsonify({
        'best_model': metadata['best_model'],
        'model_results': metadata['model_results'],
        'feature_importance': metadata['feature_importance'],
        'confusion_matrix': metadata['confusion_matrix'],
    })


if __name__ == '__main__':
    print("Starting Retento.ai API...")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
