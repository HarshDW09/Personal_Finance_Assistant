import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import pickle
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinanceModelTrainer:
    def __init__(self, data_path=None):
        self.model = None
        self.metrics = {}
        self.data_path = data_path or "data/finance_data.csv"
        
    def generate_sample_data(self, n_samples=1000):
        """Generate synthetic data for training"""
        np.random.seed(42)
        
        data = {
            "past_spending_1": np.random.normal(1200, 200, n_samples),
            "past_spending_2": np.random.normal(1100, 180, n_samples),
            "past_spending_3": np.random.normal(1300, 220, n_samples),
            "upcoming_commitments": np.random.normal(500, 100, n_samples),
        }
        
        # Create target variable with some realistic relationships
        data["monthly_expense"] = (
            0.4 * data["past_spending_1"] +
            0.3 * data["past_spending_2"] +
            0.2 * data["past_spending_3"] +
            0.8 * data["upcoming_commitments"] +
            np.random.normal(100, 50, n_samples)  # Add some noise
        )
        
        df = pd.DataFrame(data)
        
        # Ensure no negative values
        for column in df.columns:
            df[column] = df[column].clip(lower=0)
            
        return df
    
    def prepare_data(self, df=None):
        """Prepare data for training"""
        if df is None:
            if os.path.exists(self.data_path):
                df = pd.read_csv(self.data_path)
            else:
                logger.info("Generating synthetic data for training...")
                df = self.generate_sample_data()
                os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
                df.to_csv(self.data_path, index=False)
        
        X = df[["past_spending_1", "past_spending_2", "past_spending_3", "upcoming_commitments"]]
        y = df["monthly_expense"]
        
        return train_test_split(X, y, test_size=0.2, random_state=42)
    
    def train(self):
        """Train the model and calculate metrics"""
        X_train, X_test, y_train, y_test = self.prepare_data()
        
        logger.info("Training model...")
        self.model = LinearRegression()
        self.model.fit(X_train, y_train)
        
        # Calculate metrics
        y_pred = self.model.predict(X_test)
        self.metrics = {
            "r2_score": r2_score(y_test, y_pred),
            "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
            "feature_importance": dict(zip(
                ["past_1", "past_2", "past_3", "upcoming"],
                self.model.coef_
            )),
            "training_date": datetime.now().isoformat()
        }
        
        logger.info(f"Model metrics: {self.metrics}")
        
    def save_model(self, path="model.pkl"):
        """Save the trained model and metrics"""
        if self.model is None:
            raise ValueError("Model hasn't been trained yet!")
            
        model_data = {
            "model": self.model,
            "metrics": self.metrics
        }
        
        with open(path, "wb") as f:
            pickle.dump(model_data, f)
        logger.info(f"Model saved to {path}")

if __name__ == "__main__":
    trainer = FinanceModelTrainer()
    trainer.train()
    trainer.save_model("backend/model.pkl")