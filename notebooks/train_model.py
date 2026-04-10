"""
Churn Prediction - Model Training Script
Trains Logistic Regression + Random Forest, compares, saves best model.
Run: python notebooks/train_model.py
"""

import pandas as pd
import numpy as np
import joblib
import json
import os
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, roc_auc_score, classification_report,
    confusion_matrix, precision_recall_fscore_support
)
from sklearn.pipeline import Pipeline

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'telco_churn.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'model')
os.makedirs(MODEL_DIR, exist_ok=True)


def load_and_preprocess(path):
    """Load CSV, clean and encode features."""
    df = pd.read_csv(path)

    # Convert TotalCharges to numeric
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
    df['TotalCharges'].fillna(df['TotalCharges'].median(), inplace=True)

    # Drop customerID (not a feature)
    df.drop(columns=['customerID'], inplace=True, errors='ignore')

    # Encode target
    df['Churn'] = (df['Churn'] == 'Yes').astype(int)

    # Encode all object columns
    le = LabelEncoder()
    cat_cols = df.select_dtypes(include='object').columns.tolist()
    for col in cat_cols:
        df[col] = le.fit_transform(df[col].astype(str))

    return df


def train_and_evaluate(df):
    """Train multiple models, return best one."""
    X = df.drop('Churn', axis=1)
    y = df['Churn']
    feature_names = X.columns.tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    models = {
        'Logistic Regression': Pipeline([
            ('scaler', StandardScaler()),
            ('clf', LogisticRegression(max_iter=1000, random_state=42))
        ]),
        'Random Forest': Pipeline([
            ('scaler', StandardScaler()),
            ('clf', RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1))
        ]),
        'Gradient Boosting': Pipeline([
            ('scaler', StandardScaler()),
            ('clf', GradientBoostingClassifier(n_estimators=100, random_state=42))
        ]),
    }

    results = {}
    best_auc = 0
    best_name = ''
    best_model = None

    print("\n" + "="*55)
    print("  MODEL COMPARISON")
    print("="*55)

    for name, pipeline in models.items():
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        y_prob = pipeline.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_prob)
        prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='binary')

        results[name] = {
            'accuracy': round(acc, 4),
            'roc_auc': round(auc, 4),
            'precision': round(prec, 4),
            'recall': round(rec, 4),
            'f1_score': round(f1, 4),
        }
        print(f"\n{name}")
        print(f"  Accuracy : {acc:.4f}")
        print(f"  ROC-AUC  : {auc:.4f}")
        print(f"  F1 Score : {f1:.4f}")

        if auc > best_auc:
            best_auc = auc
            best_name = name
            best_model = pipeline

    print(f"\n{'='*55}")
    print(f"  Best model: {best_name} (AUC: {best_auc:.4f})")
    print("="*55)

    # Feature importance (from best model's clf step)
    clf = best_model.named_steps['clf']
    if hasattr(clf, 'feature_importances_'):
        importances = clf.feature_importances_
    elif hasattr(clf, 'coef_'):
        importances = np.abs(clf.coef_[0])
    else:
        importances = np.zeros(len(feature_names))

    feat_imp = dict(zip(feature_names, importances.tolist()))
    feat_imp_sorted = dict(sorted(feat_imp.items(), key=lambda x: x[1], reverse=True)[:15])

    # Confusion matrix
    y_pred_best = best_model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred_best).tolist()

    return best_model, best_name, results, feat_imp_sorted, cm, feature_names


def save_artifacts(model, model_name, results, feat_imp, cm, feature_names):
    """Save model and metadata."""
    joblib.dump(model, os.path.join(MODEL_DIR, 'churn_model.joblib'))

    metadata = {
        'best_model': model_name,
        'feature_names': feature_names,
        'model_results': results,
        'feature_importance': feat_imp,
        'confusion_matrix': cm,
    }
    with open(os.path.join(MODEL_DIR, 'metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"\nSaved: model/churn_model.pkl")
    print(f"Saved: model/metadata.json")


if __name__ == '__main__':
    print("Loading data...")
    df = load_and_preprocess(DATA_PATH)
    print(f"Dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"Churn rate: {df['Churn'].mean()*100:.1f}%")

    model, name, results, feat_imp, cm, features = train_and_evaluate(df)
    save_artifacts(model, name, results, feat_imp, cm, features)
    print("\nTraining complete!")
