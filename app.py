from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import pickle

app = Flask(__name__)

# Load pre-trained model (Ensure model.pkl exists in your project)
try:
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)
except FileNotFoundError:
    print("Model file not found. Ensure 'model.pkl' exists in the project folder.")

@app.route("/")
def home():
    return "Welcome to Personal Finance Assistant API!"

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        # Example input: {"past_spending": [1200, 1100, 1300], "upcoming_commitments": [500]}
        past_spending = data["past_spending"]
        upcoming_commitments = data["upcoming_commitments"]
        
        # Combine features
        features = np.array(past_spending + upcoming_commitments).reshape(1, -1)
        
        # Predict
        prediction = model.predict(features)
        return jsonify({"predicted_expenses": prediction.tolist()})
    except KeyError:
        return jsonify({"error": "Invalid input format. Expected 'past_spending' and 'upcoming_commitments'"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
