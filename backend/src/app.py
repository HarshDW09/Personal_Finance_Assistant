from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
from datetime import datetime
import numpy as np

app = Flask(__name__)
CORS(app)

# Load the trained model
try:
    model = joblib.load('model.pkl')
except:
    model = None

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/predict', methods=['POST'])
def predict_expenses():
    try:
        data = request.json
        
        # Extract past spending and upcoming commitments
        past_spending = data.get('past_spending', [])
        upcoming_commitments = data.get('upcoming_commitments', [])
        
        # Calculate features for the model
        input_data = pd.DataFrame([{
            'income': np.mean(past_spending) if past_spending else 0,  # Use average past spending as income proxy
            'month': datetime.now().month,
            'recurring_expenses': sum(upcoming_commitments) if upcoming_commitments else 0,
            'past_average_spending': np.mean(past_spending) if past_spending else 0
        }])
        
        # Make prediction
        if model:
            prediction = model.predict(input_data)[0]
            confidence = getattr(model, 'predict_proba', lambda x: [[0.5]])(input_data)[0].max()
            
            return jsonify({
                'predicted_expenses': [float(prediction)],
                'confidence': float(confidence)
            })
        else:
            # Fallback if model isn't loaded
            avg_spending = np.mean(past_spending) if past_spending else 0
            return jsonify({
                'predicted_expenses': [float(avg_spending)],
                'confidence': 0.5
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)