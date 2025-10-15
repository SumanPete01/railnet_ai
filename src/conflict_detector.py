import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pickle

class ConflictDetector:
    def __init__(self):
        self.model = None
        self.feature_names = [
            'train1_speed', 'train2_speed', 'distance_between', 
            'time_to_collision', 'track_segment', 'priority_diff'
        ]
    
    def create_conflict_data(self, n_samples=1500):
        """Create data for conflict prediction"""
        np.random.seed(42)
        
        data = []
        for i in range(n_samples):
            # Simulate two trains approaching each other
            train1_speed = np.random.uniform(40, 100)  # km/h
            train2_speed = np.random.uniform(40, 100)
            distance_between = np.random.uniform(1, 50)  # km
            time_to_collision = distance_between / (train1_speed + train2_speed) * 60  # minutes
            track_segment = np.random.randint(1, 10)  # Which part of track
            priority_diff = abs(np.random.randint(1, 4) - np.random.randint(1, 4))  # Priority difference
            
            # Determine if conflict will occur (based on realistic rules)
            will_conflict = 0
            if time_to_collision < 30:  # Less than 30 minutes to collision
                if distance_between < 20:  # And close together
                    will_conflict = 1
                elif priority_diff == 0 and time_to_collision < 15:  # Same priority, very close
                    will_conflict = 1
            
            # Add some randomness to make it realistic
            if np.random.random() < 0.1:  # 10% random conflicts
                will_conflict = 1
            if np.random.random() < 0.1:  # 10% random non-conflicts
                will_conflict = 0
                
            data.append([
                train1_speed, train2_speed, distance_between, 
                time_to_collision, track_segment, priority_diff, will_conflict
            ])
        
        columns = self.feature_names + ['will_conflict']
        return pd.DataFrame(data, columns=columns)
    
    def train_model(self, data):
        """Train classifier to predict conflicts"""
        X = data[self.feature_names]
        y = data['will_conflict']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        print(f"✅ Conflict model trained! Train Accuracy: {train_score:.3f}, Test Accuracy: {test_score:.3f}")
        return test_score
    
    def predict_conflict(self, train1, train2, distance, time_to_meeting):
        """Predict if two trains will conflict"""
        if self.model is None:
            raise ValueError("Conflict model not trained yet!")
        
        features = np.array([[
            train1['speed'],
            train2['speed'],
            distance,
            time_to_meeting,
            train1['track_segment'],
            abs(train1['priority'] - train2['priority'])
        ]])
        
        probability = self.model.predict_proba(features)[0][1]  # Probability of conflict
        return probability > 0.7, probability  # Returns (will_conflict, confidence)
    
    def save_model(self, filename="conflict_detector.pkl"):
        """Save trained model"""
        if self.model is not None:
            with open(f"models/{filename}", 'wb') as f:
                pickle.dump(self.model, f)
            print(f"✅ Conflict model saved as models/{filename}")
    
    def load_model(self, filename="conflict_detector.pkl"):
        """Load trained model"""
        try:
            with open(f"models/{filename}", 'rb') as f:
                self.model = pickle.load(f)
            print(f"✅ Conflict model loaded from models/{filename}")
        except FileNotFoundError:
            print("❌ Conflict model file not found. Train a model first.")