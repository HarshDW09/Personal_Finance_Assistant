import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import pickle

# Generate example data
data = {
    "past_spending_1": [1200, 1100, 1300, 1000, 1400],
    "past_spending_2": [1100, 1000, 1200, 900, 1300],
    "past_spending_3": [1300, 1200, 1400, 1100, 1500],
    "upcoming_commitments": [500, 400, 600, 300, 700],
    "monthly_expense": [2000, 1800, 2300, 1600, 2500],
}

df = pd.DataFrame(data)

# Train the model
X = df[["past_spending_1", "past_spending_2", "past_spending_3", "upcoming_commitments"]]
y = df["monthly_expense"]

model = LinearRegression()
model.fit(X, y)

# Save the model
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model training complete and saved as 'model.pkl'.")
