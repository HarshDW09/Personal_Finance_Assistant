import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { DollarSign, TrendingUp, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription } from "@/components/ui/alert";

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const FinanceAssistant = () => {
  const [pastSpending, setPastSpending] = useState(['', '', '']);
  const [upcomingCommitment, setUpcomingCommitment] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const spendingData = pastSpending.map((amount, index) => ({
    month: `Month ${index + 1}`,
    amount: parseFloat(amount) || 0
  }));

  const handlePredict = async () => {
    setLoading(true);
    setError(null);
    
    // Validate inputs
    const validSpending = pastSpending.every(val => val !== '' && !isNaN(parseFloat(val)));
    const validCommitment = upcomingCommitment !== '' && !isNaN(parseFloat(upcomingCommitment));

    if (!validSpending || !validCommitment) {
      setError("Please fill in all fields with valid numbers");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_URL}/api/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          past_spending: pastSpending.map(val => parseFloat(val)),
          upcoming_commitments: [parseFloat(upcomingCommitment)]
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get prediction');
      }

      const data = await response.json();
      setPrediction(data.predicted_expenses[0]);
    } catch (error) {
      console.error('Error:', error);
      setError("Failed to get prediction. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <h1 className="text-3xl font-bold mb-8">Personal Finance Assistant</h1>
      
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Past Spending Input</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {pastSpending.map((value, index) => (
              <div key={index} className="flex items-center space-x-2">
                <DollarSign className="text-gray-400" size={20} />
                <Input
                  type="number"
                  placeholder={`Month ${index + 1} spending`}
                  value={value}
                  onChange={(e) => {
                    const newSpending = [...pastSpending];
                    newSpending[index] = e.target.value;
                    setPastSpending(newSpending);
                  }}
                  className="flex-1"
                />
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Upcoming Commitments</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center space-x-2">
              <AlertCircle className="text-gray-400" size={20} />
              <Input
                type="number"
                placeholder="Expected commitment amount"
                value={upcomingCommitment}
                onChange={(e) => setUpcomingCommitment(e.target.value)}
                className="flex-1"
              />
            </div>
            <Button 
              onClick={handlePredict}
              className="w-full"
              disabled={loading}
            >
              {loading ? 'Calculating...' : 'Predict Expenses'}
            </Button>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Spending Trends</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={spendingData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="amount" 
                  stroke="#2563eb"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {prediction && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="text-blue-500" />
              Predicted Monthly Expenses
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-blue-600">
              ${prediction.toFixed(2)}
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default FinanceAssistant;