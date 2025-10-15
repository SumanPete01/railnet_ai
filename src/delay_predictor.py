import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pickle
import os

class DelayPredictor:
    def __init__(self):
        self.model = None
        self.feature_names = ['hour_of_day', 'day_of_week', 'priority', 'weather_score', 'track_occupancy']
        
    def create_synthetic_data(self, n_samples=1000):
        """Create realistic railway delay data"""
        np.random.seed(42)
        
        data = []
        for i in range(n_samples):
            # Features
            hour = np.random.randint(0, 24)
            day_of_week = np.random.randint(0, 7)
            priority = np.random.randint(1, 4)  # 1=High, 3=Low
            weather = np.random.uniform(0, 1)   # 0=Good, 1=Bad
            occupancy = np.random.uniform(0.1, 0.9)
            
            # Simulate delay based on features
            base_delay = max(0, np.random.normal(0, 10))
            weather_impact = weather * 20  # Bad weather adds delay
            occupancy_impact = occupancy * 15  # High occupancy adds delay
            priority_impact = (4 - priority) * 5  # Low priority trains get more delay
            
            total_delay = base_delay + weather_impact + occupancy_impact + priority_impact
            
            data.append([hour, day_of_week, priority, weather, occupancy, total_delay])
        
        columns = self.feature_names + ['delay_minutes']
        return pd.DataFrame(data, columns=columns)
    
    def train_model(self, data):
        """Train Random Forest model to predict delays"""
        X = data[self.feature_names]
        y = data['delay_minutes']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        print(f"✅ Model trained! Train R²: {train_score:.3f}, Test R²: {test_score:.3f}")
        return test_score
    
    def predict_delay(self, features):
        """Predict delay for given features"""
        if self.model is None:
            raise ValueError("Model not trained yet!")
        
        # Ensure features are in correct order
        feature_array = np.array([[
            features['hour_of_day'],
            features['day_of_week'], 
            features['priority'],
            features['weather_score'],
            features['track_occupancy']
        ]])
        
        prediction = self.model.predict(feature_array)[0]
        return max(0, prediction)  # No negative delays
    
    def save_model(self, filename="delay_predictor.pkl"):
        """Save trained model to file"""
        if self.model is not None:
            with open(f"models/{filename}", 'wb') as f:
                pickle.dump(self.model, f)
            print(f"✅ Model saved as models/{filename}")
    
    def load_model(self, filename="delay_predictor.pkl"):
        """Load trained model from file"""
        try:
            with open(f"models/{filename}", 'rb') as f:
                self.model = pickle.load(f)
            print(f"✅ Model loaded from models/{filename}")
        except FileNotFoundError:
            print("❌ Model file not found. Train a model first.")