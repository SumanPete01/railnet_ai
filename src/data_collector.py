import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class DataCollector:
    def __init__(self):
        self.historical_data = []
    
    def generate_training_data(self, num_samples=1000):
        """Generate synthetic training data for AI models"""
        data = []
        
        for i in range(num_samples):
            sample = {
                'timestamp': datetime.now() - timedelta(hours=np.random.randint(0, 720)),
                'train_id': np.random.randint(1, 100),
                'priority': np.random.randint(1, 4),
                'hour_of_day': np.random.randint(0, 24),
                'day_of_week': np.random.randint(0, 7),
                'weather_score': np.random.uniform(0, 1),
                'current_delay': max(0, np.random.normal(0, 30)),  # Normal distribution around 0
                'track_occupancy': np.random.uniform(0.1, 0.9),
                'future_delay': max(0, np.random.normal(0, 45))  # What we want to predict
            }
            data.append(sample)
        
        return pd.DataFrame(data)
    
    def save_data(self, filename="training_data.csv"):
        df = self.generate_training_data()
        df.to_csv(f"data/{filename}", index=False)
        print(f"Generated {len(df)} training samples")