# Configuration for AI Railway System
class Config:
    # AI Model Parameters
    LSTM_UNITS = 64
    BATCH_SIZE = 32
    EPOCHS = 100
    LEARNING_RATE = 0.001
    
    # Railway Simulation Parameters
    NUM_TRAINS = 8
    NUM_STATIONS = 6
    SIMULATION_TIME = 24 * 60  # 24 hours in minutes
    
    # File Paths
    DATA_PATH = "data/"
    MODELS_PATH = "models/"
    
    # Feature Engineering
    FEATURE_NAMES = [
        'hour_of_day', 'day_of_week', 'train_priority', 
        'current_delay', 'weather_condition', 'track_occupancy'
    ]