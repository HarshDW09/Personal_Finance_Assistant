# backend/src/train_model.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib

def generate_synthetic_data(n_samples=1000):
    np.random.seed(42)
    
    # Generate synthetic data
    data = {
        'income': np.random.normal(5000, 1000, n_samples),
        'month': np.random.randint(1, 13, n_samples),
        'recurring_expenses': np.random.normal(2000, 500, n_samples),
        'past_average_spending': np.random.normal(3000, 700, n_samples),
        'actual_expenses': np.zeros(n_samples)
    }
    
    # Create realistic relationships
    for i in range(n_samples):
        base_expense = 0.6 * data['income'][i] + 0.8 * data['recurring_expenses'][i]
        seasonal_factor = 1 + 0.1 * np.sin(2 * np.pi * data['month'][i] / 12)
        noise = np.random.normal(0, 200)
        data['actual_expenses'][i] = base_expense * seasonal_factor + noise
    
    return pd.DataFrame(data)

def train_model():
    # Generate or load your training data
    df = generate_synthetic_data()
    
    # Prepare features and target
    X = df[['income', 'month', 'recurring_expenses', 'past_average_spending']]
    y = df['actual_expenses']
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train the model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Save the model
    joblib.dump(model, 'model.pkl')
    
    # Print model performance
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    print(f"Train R² score: {train_score:.4f}")
    print(f"Test R² score: {test_score:.4f}")

if __name__ == "__main__":
    train_model()