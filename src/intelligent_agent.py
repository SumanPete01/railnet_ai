import numpy as np
from datetime import datetime, timedelta

class IntelligentAgent:
    def __init__(self, delay_predictor, conflict_detector):
        self.delay_predictor = delay_predictor
        self.conflict_detector = conflict_detector
        self.decision_log = []
        self.problems_solved = 0
        
    def perceive_environment(self, railway_state):
        """Perceive current railway situation using AI models"""
        perceptions = {
            'current_time': railway_state['current_time'],
            'trains': [],
            'predicted_problems': [],
            'recommended_actions': []
        }
        
        # Analyze each train's situation
        for train in railway_state['trains']:
            train_analysis = self._analyze_train_situation(train, railway_state)
            perceptions['trains'].append(train_analysis)
            
            # Predict future delays for this train
            delay_prediction = self._predict_train_delay(train, railway_state)
            if delay_prediction['predicted_delay'] > 20:  # Significant delay predicted
                perceptions['predicted_problems'].append({
                    'type': 'FUTURE_DELAY',
                    'train': train,
                    'predicted_delay': delay_prediction['predicted_delay'],
                    'confidence': delay_prediction['confidence']
                })
        
        # Detect potential conflicts
        conflict_predictions = self._predict_conflicts(railway_state)
        perceptions['predicted_problems'].extend(conflict_predictions)
        
        return perceptions
    
    def _analyze_train_situation(self, train, railway_state):
        """Analyze a single train's current situation"""
        return {
            'id': train.id,
            'name': train.name,
            'current_status': 'DELAYED' if train.delay > 0 else 'ON_TIME',
            'current_delay': train.delay,
            'position': train.position,
            'speed': train.speed,
            'priority': train.priority,
            'track': train.track
        }
    
    def _predict_train_delay(self, train, railway_state):
        """Use AI to predict future delays for a train"""
        # Extract features for delay prediction
        features = {
            'hour_of_day': railway_state['current_time'].hour,
            'day_of_week': railway_state['current_time'].weekday(),
            'priority': train.priority,
            'weather_score': railway_state.get('weather_score', 0.3),  # Default to good weather
            'track_occupancy': railway_state.get('track_occupancy', 0.5)
        }
        
        try:
            predicted_delay = self.delay_predictor.predict_delay(features)
            confidence = 0.8  # Based on model accuracy
        except:
            predicted_delay = 0
            confidence = 0.5
            
        return {
            'predicted_delay': predicted_delay,
            'confidence': confidence,
            'features_used': features
        }
    
    def _predict_conflicts(self, railway_state):
        """Use AI to predict potential conflicts"""
        conflicts = []
        trains = railway_state['trains']
        
        for i, train1 in enumerate(trains):
            for train2 in trains[i+1:]:
                if train1.track == train2.track:  # Only check trains on same track
                    distance = abs(train1.position - train2.position)
                    if distance < 0.2:  # Only check trains close to each other
                        time_to_meeting = distance / ((train1.speed + train2.speed) / 60) 
                        
                        train1_info = {
                            'speed': train1.speed,
                            'track_segment': 1,  # Simplified for demo
                            'priority': train1.priority
                        }
                        train2_info = {
                            'speed': train2.speed,
                            'track_segment': 1,
                            'priority': train2.priority
                        }
                        
                        will_conflict, confidence = self.conflict_detector.predict_conflict(
                            train1_info, train2_info, distance, time_to_meeting
                        )
                        
                        if will_conflict:
                            conflicts.append({
                                'type': 'POTENTIAL_CONFLICT',
                                'train1': train1,
                                'train2': train2,
                                'distance_km': distance,
                                'time_to_collision_min': time_to_meeting,
                                'confidence': confidence
                            })
        
        return conflicts
    
    def reason_and_plan(self, perceptions):
        """Generate intelligent solutions based on perceptions"""
        solutions = []
        
        for problem in perceptions['predicted_problems']:
            if problem['type'] == 'FUTURE_DELAY':
                solutions.extend(self._generate_delay_solutions(problem))
            elif problem['type'] == 'POTENTIAL_CONFLICT':
                solutions.extend(self._generate_conflict_solutions(problem))
        
        # Sort solutions by effectiveness (impact score)
        solutions.sort(key=lambda x: x['impact_score'])
        return solutions
    
    def _generate_delay_solutions(self, problem):
        """Generate solutions for delay problems"""
        train = problem['train']
        solutions = []
        
        # Solution 1: Speed adjustment
        solutions.append({
            'type': 'SPEED_ADJUSTMENT',
            'description': f"Increase {train.name} speed by 10% to recover time",
            'action': lambda: setattr(train, 'speed', min(120, train.speed * 1.1)),
            'impact_score': 30,  # Lower is better
            'confidence': 0.7
        })
        
        # Solution 2: Track switching for faster route
        if train.track != 'express_line':
            solutions.append({
                'type': 'TRACK_SWITCH',
                'description': f"Switch {train.name} to express line for faster travel",
                'action': lambda: [setattr(train, 'track', 'express_line'), 
                                 setattr(train, 'position', train.position * 0.8)],
                'impact_score': 25,
                'confidence': 0.8
            })
        
        return solutions
    
    def _generate_conflict_solutions(self, problem):
        """Generate solutions for conflict problems"""
        train1, train2 = problem['train1'], problem['train2']
        solutions = []
        
        # Solution 1: Hold lower priority train
        if train1.priority != train2.priority:
            hold_train = train1 if train1.priority > train2.priority else train2
            allow_train = train2 if hold_train == train1 else train1
            
            solutions.append({
                'type': 'HOLD_TRAIN',
                'description': f"Hold {hold_train.name} to allow {allow_train.name} to pass",
                'action': lambda: setattr(hold_train, 'delay', 10),  # Hold for 10 minutes
                'impact_score': 40,
                'confidence': 0.9
            })
        
        # Solution 2: Reroute one train to different track
        available_tracks = ['main_line', 'loop_line', 'express_line']
        other_tracks = [t for t in available_tracks if t != train1.track]
        
        if other_tracks:
            new_track = other_tracks[0]
            solutions.append({
                'type': 'REROUTE_TRAIN',
                'description': f"Reroute {train1.name} to {new_track} to avoid conflict",
                'action': lambda: [setattr(train1, 'track', new_track),
                                 setattr(train1, 'position', train1.position * 0.9)],
                'impact_score': 20,
                'confidence': 0.85
            })
        
        return solutions
    
    def execute_best_solution(self, solutions, railway_state):
        """Autonomously execute the best solution"""
        if not solutions:
            return {"action_taken": "NO_ACTION", "reason": "No problems detected"}
        
        best_solution = solutions[0]  # Already sorted by impact_score
        
        # Execute the action
        try:
            action_result = best_solution['action']()
            
            # Log the decision
            decision_record = {
                'timestamp': datetime.now(),
                'problem_type': solutions[0]['type'] if solutions else 'NONE',
                'action_taken': best_solution['description'],
                'impact_score': best_solution['impact_score'],
                'confidence': best_solution['confidence'],
                'result': 'EXECUTED'
            }
            self.decision_log.append(decision_record)
            self.problems_solved += 1
            
            return {
                "action_taken": best_solution['description'],
                "impact_score": best_solution['impact_score'],
                "confidence": best_solution['confidence'],
                "problems_solved": self.problems_solved
            }
            
        except Exception as e:
            return {"action_taken": "FAILED", "error": str(e)}
    
    def get_agent_status(self):
        """Get current status of the intelligent agent"""
        return {
            'total_decisions_made': len(self.decision_log),
            'problems_solved': self.problems_solved,
            'last_decision': self.decision_log[-1] if self.decision_log else {"action_taken": "None"},
            'agent_uptime': 'ACTIVE'
        }