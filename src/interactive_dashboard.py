

import pygame
import random
from datetime import datetime

class InteractiveDashboard:
    def __init__(self, width=1500, height=1000):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("RailNet AI - Clean Interactive Simulation")
        self.clock = pygame.time.Clock()
        
        # Initialize fonts
        try:
            self.font = pygame.font.Font(None, 24)
            self.medium_font = pygame.font.Font(None, 28)
            self.large_font = pygame.font.Font(None, 34)
            self.title_font = pygame.font.Font(None, 48)
            self.small_font = pygame.font.Font(None, 20)
        except:
            self.font = pygame.font.Font(None, 24)
            self.medium_font = pygame.font.Font(None, 28)
            self.large_font = pygame.font.Font(None, 36)
            self.title_font = pygame.font.Font(None, 48)
            self.small_font = pygame.font.Font(None, 20)
        
        # Simulation state
        self.simulation_speed = 1
        self.auto_problems = False  # Disabled by default - user controlled only
        self.last_problem_time = datetime.now()
        self.message_queue = []
        self.animation_frame = 0
        self.train_label_positions = {}  # Track label positions to prevent overlap
        
    def draw_complete_dashboard(self, visual_railway, trains, agent_status, problems, last_action):
        """Enhanced dashboard with clean UI and no overlapping labels"""
        try:
            self.screen.fill((240, 248, 255))  # Alice blue background
            self.animation_frame += 1
            
            # Draw title with simulation info
            self._draw_enhanced_title(agent_status)
            
            # Draw railway network
            if visual_railway:
                visual_railway.draw_network(self.screen)
            
            # Draw trains with clean, non-overlapping labels
            if trains:
                self._draw_clean_trains_with_side_panel(visual_railway, trains)
            
            # Draw comprehensive panels
            self._draw_train_schedule_panel(50, 550, trains)
            self._draw_notification_panel(600, 550, agent_status)
            self._draw_control_panel(50, 720)
            self._draw_agent_status(520, 720, agent_status, last_action)
            self._draw_system_metrics(50, 880, trains, problems, agent_status)
            self._draw_problems_panel(50, 950, problems)
            
            pygame.display.flip()
            
        except Exception as e:
            print(f"Dashboard error: {e}")
            self._draw_error_screen(str(e))
    
    def _draw_enhanced_title(self, agent_status):
        """Enhanced title with simulation timing"""
        title = self.title_font.render("RailNet AI - Clean User-Controlled Simulation", True, (0, 50, 100))
        self.screen.blit(title, (50, 15))
        
        # Simulation time display
        sim_time = agent_status.get('simulation_time_minutes', 0) if agent_status else 0
        time_text = self.large_font.render(f"Simulation Time: {sim_time:.1f} minutes", True, (100, 0, 100))
        self.screen.blit(time_text, (50, 60))
        
        # User control indicator
        control_text = self.medium_font.render("USER-CONTROLLED MODE (No Auto Problems)", True, (0, 150, 0))
        self.screen.blit(control_text, (50, 85))
        
        # Status indicator
        status_color = (0, 255, 0) if self.animation_frame % 60 < 30 else (0, 200, 0)
        pygame.draw.circle(self.screen, status_color, (1400, 40), 10)
        status_text = self.medium_font.render("LIVE", True, (0, 150, 0))
        self.screen.blit(status_text, (1320, 65))
    
    def _draw_clean_trains_with_side_panel(self, visual_railway, trains):
        """Draw trains with clean visualization and side panel for detailed info"""
        try:
            # Reset label positions for this frame
            self.train_label_positions = {}
            used_positions = set()
            
            # Draw trains on tracks with minimal labels
            for train in trains:
                if not hasattr(train, 'track') or not hasattr(train, 'position'):
                    continue
                    
                position = visual_railway.get_track_position(train.track, train.position)
                
                if position:
                    # Enhanced visual states
                    if not getattr(train, 'has_started', True):
                        color = (150, 150, 150)
                        size = 8
                    elif getattr(train, 'destination_reached', False):
                        color = (0, 200, 0)
                        size = 12
                    elif getattr(train, 'is_stopped', False):
                        color = (255, 0, 0) if self.animation_frame % 20 < 10 else (200, 0, 0)
                        size = 15
                    elif getattr(train, 'is_rerouting', False):
                        color = (255, 255, 0) if self.animation_frame % 40 < 20 else (200, 200, 0)
                        size = 13
                    else:
                        color = getattr(train, 'color', (0, 0, 255))
                        size = 11
                    
                    # Draw train
                    pygame.draw.circle(self.screen, color, position, size)
                    pygame.draw.circle(self.screen, (0, 0, 0), position, size, 2)
                    
                    # Draw minimal, non-overlapping label
                    self._draw_clean_train_label(train, position, used_positions)
            
            # Draw detailed train info panel on the right side
            self._draw_train_details_panel(1100, 120, trains)
            
        except Exception as e:
            print(f"Error drawing trains: {e}")
    
    def _draw_clean_train_label(self, train, position, used_positions):
        """Draw clean, non-overlapping train labels"""
        try:
            name = getattr(train, 'name', 'Unknown')
            train_id = getattr(train, 'id', 0)
            
            # Short label - just name and ID
            short_label = f"{name[:8]} #{train_id}"
            
            # Find non-overlapping position for label
            label_x, label_y = self._find_non_overlapping_label_position(
                position, short_label, used_positions
            )
            
            # Status color for text
            has_started = getattr(train, 'has_started', True)
            is_stopped = getattr(train, 'is_stopped', False)
            destination_reached = getattr(train, 'destination_reached', False)
            
            if not has_started:
                text_color = (100, 100, 100)
            elif destination_reached:
                text_color = (0, 150, 0)
            elif is_stopped:
                text_color = (200, 0, 0)
            else:
                text_color = (0, 0, 0)
            
            # Draw clean background for label
            label_surface = self.small_font.render(short_label, True, text_color)
            label_rect = label_surface.get_rect()
            label_rect.center = (label_x, label_y)
            
            # Draw subtle background
            bg_rect = label_rect.inflate(6, 4)
            pygame.draw.rect(self.screen, (255, 255, 255, 200), bg_rect, border_radius=3)
            pygame.draw.rect(self.screen, (200, 200, 200), bg_rect, 1, border_radius=3)
            
            # Draw text
            self.screen.blit(label_surface, label_rect)
            
            # Mark position as used
            used_positions.add((label_x, label_y))
            
        except Exception as e:
            print(f"Error drawing train label: {e}")
    
    def _find_non_overlapping_label_position(self, train_position, label_text, used_positions):
        """Find a position for the label that doesn't overlap with others"""
        base_x, base_y = train_position
        label_width = len(label_text) * 6  # Approximate width
        
        # Try positions around the train
        candidate_positions = [
            (base_x, base_y - 25),  # Above
            (base_x + 25, base_y - 15),  # Top right
            (base_x + 25, base_y + 15),  # Bottom right
            (base_x, base_y + 25),  # Below
            (base_x - 25, base_y + 15),  # Bottom left
            (base_x - 25, base_y - 15),  # Top left
        ]
        
        for candidate_x, candidate_y in candidate_positions:
            # Check if this position conflicts with any used position
            conflict = False
            for used_x, used_y in used_positions:
                if (abs(candidate_x - used_x) < label_width + 10 and 
                    abs(candidate_y - used_y) < 20):
                    conflict = True
                    break
            
            if not conflict:
                return candidate_x, candidate_y
        
        # If all positions conflict, use the first one with slight offset
        return candidate_positions[0][0], candidate_positions[0][1] - len(used_positions) * 5
    
    def _draw_train_details_panel(self, x, y, trains):
        """Draw detailed train information panel on the side"""
        try:
            panel_width, panel_height = 350, 420
            pygame.draw.rect(self.screen, (255, 255, 255), (x, y, panel_width, panel_height), border_radius=10)
            pygame.draw.rect(self.screen, (0, 0, 0), (x, y, panel_width, panel_height), 2, border_radius=10)
            
            title = self.medium_font.render("DETAILED TRAIN STATUS", True, (0, 100, 200))
            self.screen.blit(title, (x + 15, y + 10))
            
            if trains:
                y_offset = 35
                for i, train in enumerate(trains[:6]):  # Show up to 6 trains
                    if i * 60 + y_offset > panel_height - 60:
                        break
                    
                    train_y = y + y_offset + i * 60
                    self._draw_detailed_train_info_compact(train, x + 15, train_y)
            else:
                no_trains = self.font.render("No trains in system", True, (100, 100, 100))
                self.screen.blit(no_trains, (x + 20, y + 50))
                
        except Exception as e:
            print(f"Error drawing train details panel: {e}")
    
    def _draw_detailed_train_info_compact(self, train, x, y):
        """Draw compact detailed info for each train in the side panel"""
        try:
            name = getattr(train, 'name', 'Unknown')[:15]
            train_id = getattr(train, 'id', 0)
            has_started = getattr(train, 'has_started', True)
            delay = getattr(train, 'delay', 0)
            is_stopped = getattr(train, 'is_stopped', False)
            destination_reached = getattr(train, 'destination_reached', False)
            track = getattr(train, 'track', 'unknown')
            position = getattr(train, 'position', 0)
            priority = getattr(train, 'priority', 3)
            
            # Train name and ID
            name_text = self.font.render(f"{name} (#{train_id})", True, (0, 0, 0))
            self.screen.blit(name_text, (x, y))
            
            # Status
            if not has_started:
                start_delay = getattr(train, 'start_delay', 0)
                status = f"Waiting: {start_delay:.1f}min"
                color = (100, 100, 100)
            elif destination_reached:
                status = "Completed Journey"
                color = (0, 150, 0)
            elif is_stopped:
                stop_reason = getattr(train, 'stop_reason', 'Stopped')[:20]
                status = f"STOPPED: {stop_reason}"
                color = (200, 0, 0)
            elif delay > 0:
                status = f"DELAYED: {delay:.1f}min"
                color = (255, 100, 0)
            else:
                status = "ON TIME"
                color = (0, 150, 0)
            
            status_text = self.small_font.render(status, True, color)
            self.screen.blit(status_text, (x, y + 18))
            
            # Track and progress
            track_info = f"{track} - {position*100:.1f}% complete"
            track_text = self.small_font.render(track_info, True, (100, 100, 100))
            self.screen.blit(track_text, (x, y + 35))
            
            # Priority
            priority_colors = {1: (255, 0, 0), 2: (255, 165, 0), 3: (0, 0, 255), 4: (128, 128, 128)}
            priority_color = priority_colors.get(priority, (0, 0, 0))
            priority_text = self.small_font.render(f"Priority: {priority}", True, priority_color)
            self.screen.blit(priority_text, (x + 180, y + 35))
            
        except Exception as e:
            print(f"Error drawing compact train info: {e}")
    
    def _draw_control_panel(self, x, y):
        """Enhanced control panel emphasizing user control"""
        try:
            panel_width, panel_height = 450, 140
            pygame.draw.rect(self.screen, (255, 255, 255), (x, y, panel_width, panel_height), border_radius=10)
            pygame.draw.rect(self.screen, (0, 0, 0), (x, y, panel_width, panel_height), 2, border_radius=10)
            
            title = self.medium_font.render("USER CONTROLS (Manual Only)", True, (0, 100, 200))
            self.screen.blit(title, (x + 15, y + 10))
            
            controls = [
                "D - Add Delay to Random Train",
                "M - Track Maintenance | W - Weather Problems", 
                "S - Signal Failure    | R - Reset Simulation",
                "SPACE - Force AI Analysis | ESC - Quit",
                "No automatic problems - YOU control all events!"
            ]
            
            for i, control in enumerate(controls):
                color = (0, 150, 0) if i == 4 else (0, 0, 0)  # Highlight last line
                text = self.font.render(control, True, color)
                self.screen.blit(text, (x + 20, y + 35 + i * 20))
        except Exception as e:
            print(f"Error drawing control panel: {e}")
    
    def _draw_agent_status(self, x, y, agent_status, last_action):
        """Agent status panel"""
        try:
            panel_width, panel_height = 450, 140
            pygame.draw.rect(self.screen, (255, 255, 255), (x, y, panel_width, panel_height), border_radius=10)
            pygame.draw.rect(self.screen, (0, 0, 0), (x, y, panel_width, panel_height), 2, border_radius=10)
            
            title = self.medium_font.render("AI AGENT STATUS", True, (0, 100, 200))
            self.screen.blit(title, (x + 15, y + 10))
            
            if agent_status:
                decisions = self.font.render(f"Decisions Made: {agent_status.get('total_decisions_made', 0)}", True, (0, 0, 0))
                problems = self.font.render(f"Problems Resolved: {agent_status.get('problems_solved', 0)}", True, (0, 0, 0))
                mode = self.font.render("Mode: Reactive (User-Triggered Only)", True, (0, 150, 0))
                
                self.screen.blit(decisions, (x + 20, y + 35))
                self.screen.blit(problems, (x + 20, y + 55))
                self.screen.blit(mode, (x + 20, y + 75))
            
            if last_action:
                action_text = f"Latest: {str(last_action.get('action_taken', 'Monitoring'))[:35]}..."
                action = self.font.render(action_text, True, (0, 100, 0))
                self.screen.blit(action, (x + 20, y + 100))
        except Exception as e:
            print(f"Error drawing agent status: {e}")
    
    def _draw_train_schedule_panel(self, x, y, trains):
        """Clean train schedule panel"""
        try:
            panel_width, panel_height = 520, 150
            pygame.draw.rect(self.screen, (255, 255, 255), (x, y, panel_width, panel_height), border_radius=10)
            pygame.draw.rect(self.screen, (0, 0, 0), (x, y, panel_width, panel_height), 2, border_radius=10)
            
            title = self.medium_font.render("TRAIN SCHEDULE", True, (0, 100, 200))
            self.screen.blit(title, (x + 15, y + 10))
            
            if trains:
                y_offset = 35
                for i, train in enumerate(trains[:4]):
                    name = getattr(train, 'name', 'Unknown')[:15]
                    has_started = getattr(train, 'has_started', True)
                    start_delay = getattr(train, 'start_delay', 0)
                    
                    if has_started:
                        status = "RUNNING"
                        color = (0, 150, 0)
                    else:
                        status = f"Starts in {start_delay:.1f}min"
                        color = (100, 100, 100)
                    
                    train_info = f"{name}: {status}"
                    text = self.font.render(train_info, True, color)
                    self.screen.blit(text, (x + 20, y + y_offset + i * 25))
        except Exception as e:
            print(f"Error drawing schedule panel: {e}")
    
    def _draw_notification_panel(self, x, y, agent_status):
        """Notification panel"""
        try:
            panel_width, panel_height = 850, 150
            pygame.draw.rect(self.screen, (255, 255, 255), (x, y, panel_width, panel_height), border_radius=10)
            pygame.draw.rect(self.screen, (0, 0, 0), (x, y, panel_width, panel_height), 2, border_radius=10)
            
            title = self.medium_font.render("TRAIN COMMUNICATIONS", True, (0, 100, 200))
            self.screen.blit(title, (x + 15, y + 10))
            
            if agent_status and 'recent_notifications' in agent_status:
                notifications = agent_status['recent_notifications']
                if notifications:
                    y_offset = 35
                    for i, notif in enumerate(notifications[-4:]):
                        timestamp = notif.get('timestamp', 0)
                        from_train = notif.get('from_train', 'Unknown')[:10]
                        to_train = notif.get('to_train', 'Unknown')[:10]
                        message = notif.get('message', 'No message')[:25]
                        
                        notif_text = f"T+{timestamp:.1f}: {from_train} → {to_train}: {message}"
                        text = self.small_font.render(notif_text, True, (0, 100, 0))
                        self.screen.blit(text, (x + 20, y + y_offset + i * 20))
                else:
                    no_notif = self.font.render("No recent communications", True, (100, 100, 100))
                    self.screen.blit(no_notif, (x + 20, y + 50))
        except Exception as e:
            print(f"Error drawing notification panel: {e}")
    
    def _draw_system_metrics(self, x, y, trains, problems, agent_status):
        """System metrics panel"""
        try:
            panel_width, panel_height = 1400, 60
            pygame.draw.rect(self.screen, (255, 255, 255), (x, y, panel_width, panel_height), border_radius=8)
            pygame.draw.rect(self.screen, (0, 0, 0), (x, y, panel_width, panel_height), 2, border_radius=8)
            
            title = self.medium_font.render("SYSTEM METRICS", True, (0, 100, 200))
            self.screen.blit(title, (x + 15, y + 10))
            
            if agent_status:
                metrics = [
                    f"Total Trains: {agent_status.get('total_trains', 0)}",
                    f"Started: {agent_status.get('started_trains', 0)}",
                    f"Waiting: {agent_status.get('waiting_to_start', 0)}",
                    f"Delayed: {agent_status.get('delayed_trains', 0)}",
                    f"Completed: {agent_status.get('completed_journeys', 0)}",
                    f"Active Problems: {len(problems) if problems else 0}",
                    f"Mode: USER CONTROLLED",
                    f"Efficiency: {self._calculate_efficiency(agent_status)}"
                ]
                
                for i, metric in enumerate(metrics):
                    x_pos = x + 20 + (i * 165)
                    color = self._get_metric_color(metric)
                    text = self.font.render(metric, True, color)
                    self.screen.blit(text, (x_pos, y + 35))
        except Exception as e:
            print(f"Error drawing metrics: {e}")
    
    def _calculate_efficiency(self, agent_status):
        """Calculate system efficiency"""
        try:
            total = agent_status.get('total_trains', 1)
            on_time = agent_status.get('started_trains', 0) - agent_status.get('delayed_trains', 0)
            completed = agent_status.get('completed_journeys', 0)
            efficiency = ((on_time + completed * 1.5) / (total * 1.5)) * 100
            return f"{int(max(0, min(100, efficiency)))}%"
        except:
            return "N/A"
    
    def _get_metric_color(self, metric):
        """Get appropriate color for metrics"""
        if "Delayed" in metric or "Problems" in metric:
            return (200, 0, 0)
        elif "Completed" in metric or "Efficiency" in metric:
            return (0, 150, 0)
        elif "USER CONTROLLED" in metric:
            return (0, 100, 200)
        else:
            return (0, 0, 0)
    
    def _draw_problems_panel(self, x, y, problems):
        """Problems panel"""
        try:
            panel_width, panel_height = 1400, 45
            pygame.draw.rect(self.screen, (255, 255, 255), (x, y, panel_width, panel_height), border_radius=8)
            pygame.draw.rect(self.screen, (0, 0, 0), (x, y, panel_width, panel_height), 2, border_radius=8)
            
            title = self.medium_font.render("ACTIVE PROBLEMS", True, (200, 0, 0))
            self.screen.blit(title, (x + 15, y + 10))
            
            if problems:
                problem_texts = []
                for problem in problems[:3]:
                    problem_text = self._format_problem_enhanced(problem)
                    problem_texts.append(problem_text)
                
                combined_text = " | ".join(problem_texts)
                text = self.font.render(combined_text, True, (200, 0, 0))
                self.screen.blit(text, (x + 20, y + 25))
            else:
                no_problems = self.font.render("No active problems - system running smoothly (user-controlled mode)", True, (0, 150, 0))
                self.screen.blit(no_problems, (x + 20, y + 25))
        except Exception as e:
            print(f"Error drawing problems panel: {e}")
    
    def _format_problem_enhanced(self, problem):
        """Format problem text"""
        try:
            problem_type = problem.get('type', 'UNKNOWN')
            duration = problem.get('duration', 0)
            
            if problem_type == 'WEATHER_DELAY':
                affected = len(problem.get('affected_trains', []))
                return f"Weather: {affected} trains affected ({duration:.0f}min)"
            elif problem_type == 'SIGNAL_FAILURE':
                return f"Signal failure: cascading delays ({duration:.0f}min)"
            elif problem_type == 'TRACK_MAINTENANCE':
                track = problem.get('track', 'unknown')
                return f"Maintenance: {track} blocked ({duration:.0f}min)"
            return f"{problem_type} ({duration:.0f}min)"
        except:
            return "Problem details unavailable"
    
    def _draw_error_screen(self, error_msg):
        """Error screen fallback"""
        self.screen.fill((200, 200, 200))
        error_text = self.large_font.render(f"Dashboard Error: {error_msg[:50]}", True, (255, 0, 0))
        self.screen.blit(error_text, (50, 50))
        pygame.display.flip()
    
    def handle_interaction(self):
        """Handle user interactions - only manual triggers"""
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'QUIT'
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_d:
                        self.add_message("Manual delay added")
                        return 'ADD_DELAY'
                    elif event.key == pygame.K_m:
                        self.add_message("Track maintenance initiated")
                        return 'TRACK_MAINTENANCE'
                    elif event.key == pygame.K_w:
                        self.add_message("Weather problems activated")
                        return 'WEATHER_PROBLEM'
                    elif event.key == pygame.K_s:
                        self.add_message("Signal failure triggered")
                        return 'SIGNAL_FAILURE'
                    elif event.key == pygame.K_r:
                        self.add_message("System reset")
                        return 'RESET'
                    elif event.key == pygame.K_SPACE:
                        self.add_message("AI analysis forced")
                        return 'FORCE_AI_ACTION'
                    elif event.key == pygame.K_ESCAPE:
                        return 'QUIT'
            return None
        except Exception as e:
            print(f"Error handling interaction: {e}")
            return None
    
    def add_message(self, message):
        """Add timestamped message"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.message_queue.append(f"{timestamp}: {str(message)}")
            if len(self.message_queue) > 10:
                self.message_queue.pop(0)
        except Exception as e:
            print(f"Error adding message: {e}")
    
    def should_generate_auto_problem(self):
        """Disabled - no auto problems in user-controlled mode"""
        return False