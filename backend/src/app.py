# backend/src/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
from datetime import datetime
import json

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

@app.route('/predict', methods=['POST'])
def predict_expenses():
    try:
        data = request.json
        
        # Convert input data to DataFrame
        input_data = pd.DataFrame([{
            'income': data['income'],
            'month': datetime.strptime(data['date'], '%Y-%m').month,
            'recurring_expenses': data['recurring_expenses'],
            'past_average_spending': data['past_average_spending']
        }])
        
        # Make prediction
        if model:
            prediction = model.predict(input_data)[0]
            confidence = model.predict_proba(input_data)[0].max()
            
            return jsonify({
                'predicted_expenses': round(float(prediction), 2),
                'confidence': round(float(confidence), 2)
            })
        else:
            return jsonify({
                'error': 'Model not loaded',
                'predicted_expenses': data['past_average_spending'],
                'confidence': 0.5
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/expenses', methods=['POST'])
def add_expense():
    try:
        data = request.json
        # In a real app, you would save this to a database
        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)