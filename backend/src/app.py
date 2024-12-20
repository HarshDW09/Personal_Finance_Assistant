from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import pandas as pd
import numpy as np
import pickle
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Setup rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

class FinancePredictor:
    def __init__(self, model_path="model.pkl"):
        self.model = None
        self.metrics = None
        self.load_model(model_path)
    
    def load_model(self, model_path):
        try:
            with open(model_path, "rb") as f:
                model_data = pickle.load(f)
                self.model = model_data["model"]
                self.metrics = model_data["metrics"]
            logger.info("Model loaded successfully")
        except FileNotFoundError:
            logger.error(f"Model file not found at {model_path}")
            raise
    
    def predict(self, features):
        """Make predictions with input validation"""
        if not isinstance(features, np.ndarray):
            features = np.array(features)
        
        if features.shape[1] != 4:
            raise ValueError("Expected 4 features")
            
        prediction = self.model.predict(features)
        return prediction[0]

predictor = FinancePredictor("backend/model.pkl")

@app.route("/api/health")
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model_info": predictor.metrics
    })

@app.route("/api/predict", methods=["POST"])
@limiter.limit("50 per hour")
def predict():
    """Predict monthly expenses"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Validate input
        required_fields = ["past_spending", "upcoming_commitments"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Prepare features
        past_spending = data["past_spending"]
        upcoming_commitments = data["upcoming_commitments"]
        
        if len(past_spending) != 3 or len(upcoming_commitments) != 1:
            return jsonify({"error": "Invalid input dimensions"}), 400
            
        features = np.array(past_spending + upcoming_commitments).reshape(1, -1)
        
        # Make prediction
        prediction = predictor.predict(features)
        
        # Calculate confidence based on historical data proximity
        confidence_score = 0.85  # Simplified confidence score
        
        response = {
            "predicted_expenses": float(prediction),
            "confidence_score": confidence_score,
            "timestamp": datetime.now().isoformat(),
            "model_metrics": predictor.metrics
        }
        
        logger.info(f"Prediction made: {prediction:.2f}")
        return jsonify(response)

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/model/metrics", methods=["GET"])
def get_model_metrics():
    """Get model performance metrics"""
    return jsonify(predictor.metrics)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", False))