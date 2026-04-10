"""
Generates a synthetic Telco-style churn dataset (5000 rows).
Run this if you don't have the Kaggle CSV.
Output: data/telco_churn.csv
"""

import pandas as pd
import numpy as np
import os

np.random.seed(42)
n = 5000

df = pd.DataFrame()

df['customerID'] = [f'CUST-{i:05d}' for i in range(n)]
df['gender'] = np.random.choice(['Male', 'Female'], n)
df['SeniorCitizen'] = np.random.choice([0, 1], n, p=[0.84, 0.16])
df['Partner'] = np.random.choice(['Yes', 'No'], n)
df['Dependents'] = np.random.choice(['Yes', 'No'], n, p=[0.3, 0.7])
df['tenure'] = np.random.randint(1, 72, n)

df['PhoneService'] = np.random.choice(['Yes', 'No'], n, p=[0.9, 0.1])
df['MultipleLines'] = np.where(df['PhoneService'] == 'No', 'No phone service',
                                np.random.choice(['Yes', 'No'], n))
df['InternetService'] = np.random.choice(['DSL', 'Fiber optic', 'No'], n, p=[0.34, 0.44, 0.22])

for col in ['OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport']:
    df[col] = np.where(df['InternetService'] == 'No', 'No internet service',
                       np.random.choice(['Yes', 'No'], n))

df['StreamingTV'] = np.where(df['InternetService'] == 'No', 'No internet service',
                              np.random.choice(['Yes', 'No'], n))
df['StreamingMovies'] = np.where(df['InternetService'] == 'No', 'No internet service',
                                  np.random.choice(['Yes', 'No'], n))

df['Contract'] = np.random.choice(['Month-to-month', 'One year', 'Two year'], n, p=[0.55, 0.24, 0.21])
df['PaperlessBilling'] = np.random.choice(['Yes', 'No'], n, p=[0.59, 0.41])
df['PaymentMethod'] = np.random.choice(
    ['Electronic check', 'Mailed check', 'Bank transfer (automatic)', 'Credit card (automatic)'], n)

df['MonthlyCharges'] = np.round(np.random.uniform(18, 118, n), 2)
df['TotalCharges'] = np.round(df['tenure'] * df['MonthlyCharges'] * np.random.uniform(0.95, 1.05, n), 2)

# Churn probability influenced by key features
churn_prob = (
    0.05
    + 0.25 * (df['Contract'] == 'Month-to-month')
    + 0.10 * (df['InternetService'] == 'Fiber optic')
    + 0.08 * (df['tenure'] < 12)
    + 0.06 * (df['MonthlyCharges'] > 70)
    - 0.10 * (df['tenure'] > 48)
    - 0.05 * (df['Contract'] == 'Two year')
    + np.random.normal(0, 0.05, n)
).clip(0.02, 0.95)

df['Churn'] = np.where(np.random.random(n) < churn_prob, 'Yes', 'No')

out_path = os.path.join(os.path.dirname(__file__), 'telco_churn.csv')
df.to_csv(out_path, index=False)
print(f"Dataset saved: {out_path} ({len(df)} rows)")
print(f"Churn rate: {df['Churn'].value_counts(normalize=True)['Yes']*100:.1f}%")
