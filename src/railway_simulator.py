


import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

class Train:
    def __init__(self, id, name, priority, current_station, speed=80, track='main_line', start_delay=0):
        self.id = id
        self.name = name
        self.priority = priority
        self.base_speed = speed
        self.speed = speed
        self.current_station = current_station
        self.track = track
        self.original_track = track
        self.delay = 0
        self.position = 0.0
        self.color = self._get_train_color(priority)
        self.route_progress = 0
        self.is_stopped = False
        self.stop_reason = ""
        self.is_rerouting = False
        self.reroute_message = ""
        self.reroute_timer = 0
        self.destination_reached = False
        self.last_movement_time = datetime.now()
        
        # Enhanced attributes for clean simulation
        self.start_delay = start_delay
        self.has_started = False
        self.notification_sent = []
        self.delay_notification_received = False
        self.ahead_train_delay_info = None
        
        # User-controlled conflict flags
        self.user_delayed = False  # Only true when user manually adds delay
        self.manual_stop = False   # Only true when user manually stops train
        
    def _get_train_color(self, priority):
        colors = {
            1: (255, 0, 0),    # Red - High priority
            2: (255, 165, 0),  # Orange - Medium priority  
            3: (0, 0, 255),    # Blue - Low priority
            4: (128, 128, 128) # Gray - Goods train
        }
        return colors.get(priority, (0, 0, 0))
    
    def should_start_moving(self, current_simulation_time):
        """Check if train should start moving based on start delay"""
        if not self.has_started and current_simulation_time >= self.start_delay:
            self.has_started = True
            return True
        return self.has_started
    
    def update_position(self, time_delta_minutes, visual_railway=None, current_simulation_time=0):
        """Clean position update - only stops for user-initiated problems"""
        
        # Check if train should start moving
        if not self.should_start_moving(current_simulation_time):
            self.is_stopped = True
            self.stop_reason = f"Scheduled start in {self.start_delay - current_simulation_time:.1f} minutes"
            return
        
        # Handle rerouting animation
        if self.is_rerouting:
            self.reroute_timer -= time_delta_minutes
            if self.reroute_timer <= 0:
                self.is_rerouting = False
                self.reroute_message = ""
        
        # Only stop for user-initiated delays or manual stops
        if self.manual_stop or self.user_delayed:
            if self.delay > 0:
                self.delay = max(0, self.delay - time_delta_minutes)
                if self.delay > 0:
                    self.is_stopped = True
                    self.stop_reason = f"User delay: {self.delay:.1f}min remaining"
                    return
                else:
                    self.is_stopped = False
                    self.stop_reason = ""
                    self.user_delayed = False
        
        # Normal smooth movement when no user intervention
        if not self.destination_reached and not self.manual_stop:
            self.is_stopped = False
            self.stop_reason = ""
            
            # Smooth movement at adjusted speed
            effective_speed = self.speed * 0.1  # Adjust for visual speed
            distance_km = (effective_speed * time_delta_minutes) / 60
            track_length_km = 500
            progress_increment = distance_km / track_length_km
            
            self.position = min(0.98, self.position + progress_increment)
            
            if self.position >= 0.98:
                self.destination_reached = True
                self.is_stopped = True
                self.stop_reason = "Reached destination"
                self.speed = 0
    
    def receive_delay_notification(self, ahead_train_info):
        """Receive notification about delayed train ahead"""
        self.delay_notification_received = True
        self.ahead_train_delay_info = ahead_train_info
        print(f"Train {self.name} received delay notification about {ahead_train_info['name']}")
    
    def introduce_delay(self, delay_minutes, reason="Operational delay"):
        """Add delay with notification system - LEGACY METHOD"""
        self.delay += delay_minutes
        self.is_stopped = True
        self.stop_reason = f"{reason}: {self.delay:.1f}min"
        self.notification_sent = []
    
    def introduce_user_delay(self, delay_minutes, reason="User-initiated delay"):
        """Add delay only when triggered by user"""
        self.delay += delay_minutes
        self.user_delayed = True
        self.is_stopped = True
        self.stop_reason = f"{reason}: {self.delay:.1f}min"
        self.notification_sent = []  # Reset notifications
    
    def reroute_to_track(self, new_track, reason="Avoiding conflict"):
        """Reroute train with visual feedback"""
        if new_track != self.track:
            old_track = self.track
            self.track = new_track
            self.is_rerouting = True
            self.reroute_timer = 15
            self.reroute_message = f"Rerouted from {old_track} to {new_track}: {reason}"
            self.position = max(0, self.position - 0.02)
            print(f"REROUTING: {self.name} moved from {old_track} to {new_track} - {reason}")

class SlowRailwaySimulator:
    """User-controlled railway simulator - clean version"""
    
    def __init__(self):
        self.trains = []
        self.stations = ['Delhi', 'Ghaziabad', 'Mathura', 'Agra', 'Mumbai']
        self.current_time = datetime.now()
        self.simulation_data = []
        self.problems = []  # Only user-initiated problems
        self.problem_counter = 0
        self.simulation_minutes = 0
        self.track_capacities = {
            'main_line': 3,
            'loop_line': 2, 
            'express_line': 2
        }
        self.delay_events = []
        self.notification_log = []
        
        # User control flags
        self.auto_conflicts_disabled = True  # Key feature: no auto conflicts
        
    def add_train_with_schedule(self, train_config):
        """Add train with scheduled start time"""
        train = Train(
            train_config["id"], 
            train_config["name"], 
            train_config["priority"], 
            train_config["station"], 
            train_config["speed"], 
            train_config["track"],
            train_config.get("start_delay", 0)
        )
        self.trains.append(train)
        print(f"Scheduled: {train.name} will start in {train.start_delay} minutes on {train.track}")
    
    def add_train(self, train):
        """Maintain compatibility"""
        if hasattr(train, 'start_delay'):
            train.start_delay = 0
        else:
            train.start_delay = 0
        train.has_started = True
        self.trains.append(train)
    
    def notify_trains_behind_delayed_train(self, delayed_train):
        """Only notify if train was delayed by user action"""
        if not getattr(delayed_train, 'user_delayed', False):
            return  # Don't notify for non-user delays
        
        same_track_trains = [t for t in self.trains if t.track == delayed_train.track and t.id != delayed_train.id]
        trains_behind = [t for t in same_track_trains if t.position < delayed_train.position and not t.destination_reached]
        
        for train_behind in trains_behind:
            if train_behind.id not in delayed_train.notification_sent:
                delay_info = {
                    'id': delayed_train.id,
                    'name': delayed_train.name,
                    'delay_minutes': delayed_train.delay,
                    'position': delayed_train.position,
                    'reason': delayed_train.stop_reason
                }
                train_behind.receive_delay_notification(delay_info)
                delayed_train.notification_sent.append(train_behind.id)
                
                self.notification_log.append({
                    'timestamp': self.simulation_minutes,
                    'from_train': delayed_train.name,
                    'to_train': train_behind.name,
                    'message': f"User delay ahead: {delayed_train.delay:.1f}min",
                    'track': delayed_train.track
                })
                
                self._consider_rerouting_for_notified_train(train_behind, delayed_train)
    
    def _consider_rerouting_for_notified_train(self, notified_train, delayed_train):
        """Conservative rerouting - only for significant user-initiated delays"""
        if delayed_train.delay > 15:  # Only reroute for major delays (15+ min)
            alternative_tracks = [track for track in self.track_capacities.keys() 
                                if track != notified_train.track]
            
            for alt_track in alternative_tracks:
                trains_on_alt_track = len([t for t in self.trains if t.track == alt_track and not t.destination_reached])
                if trains_on_alt_track < self.track_capacities[alt_track]:
                    reason = f"Avoiding user delay: {delayed_train.name} ({delayed_train.delay:.1f}min)"
                    notified_train.reroute_to_track(alt_track, reason)
                    break
    
    def introduce_problem(self, train_id, delay_minutes):
        """User-triggered problem introduction only"""
        for train in self.trains:
            if train.id == train_id:
                reason = "User-initiated delay"
                if hasattr(train, 'introduce_user_delay'):
                    train.introduce_user_delay(delay_minutes, reason)
                else:
                    # Fallback for compatibility
                    train.introduce_delay(delay_minutes, reason)
                    train.user_delayed = True
                
                self.delay_events.append({
                    'train_id': train_id,
                    'train_name': train.name,
                    'delay_minutes': delay_minutes,
                    'reason': reason,
                    'timestamp': self.simulation_minutes,
                    'user_initiated': True,
                    'resolved': False
                })
                
                # Notify trains behind this delayed train
                self.notify_trains_behind_delayed_train(train)
                print(f"USER DELAY: {train.name} delayed by {delay_minutes} minutes")
                return True
        return False
    
    def simulate_time_step(self, minutes=0.5, visual_railway=None):
        """Clean simulation - no auto conflicts, smooth operation"""
        self.current_time += timedelta(minutes=minutes)
        self.simulation_minutes += minutes
        
        # Update train positions - smooth movement unless user intervened
        for train in self.trains:
            train.update_position(minutes, visual_railway, self.simulation_minutes)
        
        # Only resolve conflicts if they were user-initiated
        conflicts = self._detect_user_initiated_conflicts_only()
        
        # Only send notifications for user-triggered delays
        self._check_user_delay_notifications()
        
        # Update delay events
        self._update_delay_events()
        
        # Remove expired problems
        self.problems = [p for p in self.problems if p.get('duration', 0) > 0]
        for problem in self.problems:
            problem['duration'] -= minutes
        
        self.record_simulation_state(conflicts)
        return conflicts
    
    def _check_user_delay_notifications(self):
        """Only check notifications for user-delayed trains"""
        for train in self.trains:
            user_delayed = getattr(train, 'user_delayed', False)
            if train.delay > 0 and user_delayed and train.is_stopped:
                self.notify_trains_behind_delayed_train(train)
    
    def _detect_user_initiated_conflicts_only(self):
        """Only detect conflicts that result from user actions"""
        conflicts = []
        
        trains_by_track = {}
        for train in self.trains:
            if not train.destination_reached and train.has_started:
                if train.track not in trains_by_track:
                    trains_by_track[train.track] = []
                trains_by_track[train.track].append(train)
        
        for track, trains in trains_by_track.items():
            trains.sort(key=lambda t: t.position)
            
            for i in range(len(trains) - 1):
                train1 = trains[i]
                train2 = trains[i + 1]
                distance = train2.position - train1.position
                
                if distance < 0.05 and not train1.destination_reached:
                    user_delay_involved = (getattr(train1, 'user_delayed', False) or 
                                         getattr(train2, 'user_delayed', False))
                    
                    if user_delay_involved:  # Only conflicts from user actions
                        conflicts.append({
                            'train1': train1,
                            'train2': train2,
                            'track': track,
                            'distance': distance,
                            'severity': 'USER_INITIATED'
                        })
                        
                        # Resolve by priority
                        if train1.priority < train2.priority:
                            train2.manual_stop = True
                            train2.is_stopped = True
                            train2.stop_reason = f"Yielding to {train1.name} (user delay conflict)"
                        else:
                            train1.manual_stop = True
                            train1.is_stopped = True
                            train1.stop_reason = f"Yielding to {train2.name} (user delay conflict)"
                
                elif distance >= 0.08:
                    # Resume movement when safe
                    for train in [train1, train2]:
                        if (getattr(train, 'manual_stop', False) and 
                            "Yielding to" in train.stop_reason):
                            train.manual_stop = False
                            train.is_stopped = False
                            train.stop_reason = ""
        
        return conflicts
    
    def _update_delay_events(self):
        """Update user-initiated delay events"""
        for event in self.delay_events:
            if not event['resolved'] and event.get('user_initiated', False):
                train = next((t for t in self.trains if t.id == event['train_id']), None)
                if train and train.delay <= 0 and not getattr(train, 'user_delayed', False):
                    event['resolved'] = True
    
    def introduce_random_problem(self):
        """DISABLED - No random problems in user-controlled mode"""
        print("Random problems disabled - user-controlled mode only")
        return "NO_AUTO_PROBLEMS"
    
    def _add_weather_delay(self):
        """User-triggered weather delay"""
        active_trains = [t for t in self.trains if not t.destination_reached and t.has_started]
        if not active_trains:
            return
            
        affected_trains = random.sample(active_trains, min(2, len(active_trains)))
        
        for train in affected_trains:
            delay_amount = random.randint(15, 35)
            if hasattr(train, 'introduce_user_delay'):
                train.introduce_user_delay(delay_amount, "User weather delay")
            else:
                train.introduce_delay(delay_amount, "User weather delay")
                train.user_delayed = True
            self.notify_trains_behind_delayed_train(train)
        
        self.problems.append({
            'type': 'WEATHER_DELAY', 
            'duration': 30,
            'affected_trains': [t.name for t in affected_trains],
            'user_initiated': True
        })
        print(f"USER WEATHER EVENT: Affected {len(affected_trains)} trains")
    
    def _add_signal_failure(self):
        """User-triggered signal failure"""
        active_trains = [t for t in self.trains if not t.destination_reached and t.has_started]
        if not active_trains:
            return
            
        primary_train = random.choice(active_trains)
        primary_delay = random.randint(25, 50)
        
        if hasattr(primary_train, 'introduce_user_delay'):
            primary_train.introduce_user_delay(primary_delay, "User signal failure")
        else:
            primary_train.introduce_delay(primary_delay, "User signal failure")
            primary_train.user_delayed = True
        
        self.notify_trains_behind_delayed_train(primary_train)
        
        self.problems.append({
            'type': 'SIGNAL_FAILURE', 
            'duration': 40,
            'user_initiated': True
        })
        print("USER SIGNAL FAILURE: Primary train delayed")
    
    def _add_track_maintenance(self):
        """User-triggered track maintenance"""
        affected_track = random.choice(['main_line', 'loop_line'])
        maintenance_trains = [t for t in self.trains 
                            if t.track == affected_track and not t.destination_reached and t.has_started]
        
        for train in maintenance_trains:
            delay_amount = random.randint(20, 40)
            if hasattr(train, 'introduce_user_delay'):
                train.introduce_user_delay(delay_amount, f"User maintenance: {affected_track}")
            else:
                train.introduce_delay(delay_amount, f"User maintenance: {affected_track}")
                train.user_delayed = True
            self.notify_trains_behind_delayed_train(train)
        
        self.problems.append({
            'type': 'TRACK_MAINTENANCE', 
            'track': affected_track, 
            'duration': 50,
            'affected_trains': [t.name for t in maintenance_trains],
            'user_initiated': True
        })
        print(f"USER MAINTENANCE: {affected_track} affected, {len(maintenance_trains)} trains delayed")
    
    def record_simulation_state(self, conflicts):
        """Record simulation state"""
        active_trains = [t for t in self.trains if not t.destination_reached]
        started_trains = [t for t in active_trains if t.has_started]
        
        state = {
            'timestamp': self.current_time,
            'simulation_minutes': self.simulation_minutes,
            'total_trains': len(self.trains),
            'active_trains': len(active_trains),
            'started_trains': len(started_trains),
            'delayed_trains': len([t for t in started_trains if t.delay > 0]),
            'stopped_trains': len([t for t in started_trains if t.is_stopped]),
            'completed_journeys': len([t for t in self.trains if t.destination_reached]),
            'notifications_sent': len(self.notification_log)
        }
        self.simulation_data.append(state)
    
    def get_system_status(self):
        """Enhanced system status for user-controlled mode"""
        active_trains = [t for t in self.trains if not t.destination_reached]
        started_trains = [t for t in active_trains if t.has_started]
        
        return {
            'simulation_time_minutes': self.simulation_minutes,
            'total_trains': len(self.trains),
            'active_trains': len(active_trains),
            'started_trains': len(started_trains),
            'waiting_to_start': len([t for t in active_trains if not t.has_started]),
            'delayed_trains': len([t for t in started_trains if t.delay > 0]),
            'stopped_trains': len([t for t in started_trains if t.is_stopped]),
            'rerouting_trains': len([t for t in started_trains if getattr(t, 'is_rerouting', False)]),
            'completed_journeys': len([t for t in self.trains if t.destination_reached]),
            'active_problems': len(self.problems),
            'user_control_mode': True,
            'recent_notifications': self.notification_log[-5:] if self.notification_log else []
        }

    def detect_potential_conflicts(self):
        """Maintain compatibility"""
        return self._detect_user_initiated_conflicts_only()

# Legacy compatibility classes
class RailwaySimulator(SlowRailwaySimulator):
    """Legacy compatibility"""
    pass

# Maintain backward compatibility
CleanRailwaySimulator = SlowRailwaySimulator