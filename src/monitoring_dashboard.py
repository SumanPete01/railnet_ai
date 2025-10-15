import pygame
import sys
from datetime import datetime

class MonitoringDashboard:
    def __init__(self, width=1000, height=700):
        # Initialize pygame if not already initialized
        if not pygame.get_init():
            pygame.init()
            
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("RailNet AI - Intelligent Agent Dashboard")
        self.clock = pygame.time.Clock()
        
        # Initialize fonts after pygame.init()
        self.font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 36)
        
        self.agent_data = {}
        self.railway_data = {}
        self.last_action = {}
        
    def update_data(self, agent_status, railway_state, last_action):
        """Update dashboard with latest data"""
        self.agent_data = agent_status or {}
        self.railway_data = railway_state or {}
        self.last_action = last_action or {}
        
    def draw_dashboard(self):
        """Draw the complete monitoring dashboard"""
        self.screen.fill((240, 240, 240))  # Light gray background
        
        # Title
        title = self.large_font.render("🚉 RAILNET INTELLIGENT AGENT DASHBOARD", True, (0, 0, 0))
        self.screen.blit(title, (50, 20))
        
        # Agent Status Panel
        self._draw_agent_panel(50, 80)
        
        # Railway Status Panel
        self._draw_railway_panel(50, 250)
        
        # Action Log Panel
        self._draw_action_panel(50, 450)
        
        pygame.display.flip()
        
    def _draw_agent_panel(self, x, y):
        """Draw agent status panel"""
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, 900, 150), border_radius=10)
        pygame.draw.rect(self.screen, (0, 0, 0), (x, y, 900, 150), 2, border_radius=10)
        
        title = self.font.render("🤖 INTELLIGENT AGENT STATUS", True, (0, 100, 200))
        self.screen.blit(title, (x + 20, y + 20))
        
        decisions = self.font.render(f"Decisions Made: {self.agent_data.get('total_decisions_made', 0)}", True, (0, 0, 0))
        problems = self.font.render(f"Problems Solved: {self.agent_data.get('problems_solved', 0)}", True, (0, 0, 0))
        status = self.font.render(f"Status: {self.agent_data.get('agent_uptime', 'ACTIVE')}", True, (0, 150, 0))
        
        self.screen.blit(decisions, (x + 40, y + 50))
        self.screen.blit(problems, (x + 40, y + 80))
        self.screen.blit(status, (x + 40, y + 110))
    
    def _draw_railway_panel(self, x, y):
        """Draw railway status panel"""
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, 900, 180), border_radius=10)
        pygame.draw.rect(self.screen, (0, 0, 0), (x, y, 900, 180), 2, border_radius=10)
        
        title = self.font.render("🚊 RAILWAY NETWORK STATUS", True, (0, 100, 200))
        self.screen.blit(title, (x + 20, y + 20))
        
        trains = self.font.render(f"Active Trains: {len(self.railway_data.get('trains', []))}", True, (0, 0, 0))
        delayed = self.font.render(f"Delayed Trains: {sum(1 for t in self.railway_data.get('trains', []) if hasattr(t, 'delay') and t.delay > 0)}", True, (0, 0, 0))
        time = self.font.render(f"Simulation Time: {self.railway_data.get('current_time', 'Unknown')}", True, (0, 0, 0))
        
        self.screen.blit(trains, (x + 40, y + 50))
        self.screen.blit(delayed, (x + 40, y + 80))
        self.screen.blit(time, (x + 40, y + 110))
        
        # Draw simple train positions
        trains_list = self.railway_data.get('trains', [])
        for i, train in enumerate(trains_list[:4]):  # Show first 4 trains
            if hasattr(train, 'name') and hasattr(train, 'position'):
                train_info = self.font.render(f"{train.name}: Pos {train.position:.1f}km", True, (0, 0, 0))
                self.screen.blit(train_info, (x + 40, y + 140 + i * 20))
    
    def _draw_action_panel(self, x, y):
        """Draw action log panel"""
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, 900, 150), border_radius=10)
        pygame.draw.rect(self.screen, (0, 0, 0), (x, y, 900, 150), 2, border_radius=10)
        
        title = self.font.render("⚡ LAST AGENT ACTION", True, (0, 100, 200))
        self.screen.blit(title, (x + 20, y + 20))
        
        action_text = self.last_action.get('action_taken', 'No action yet')
        action = self.font.render(f"Action: {action_text}", True, (0, 100, 0))
        impact = self.font.render(f"Impact Score: {self.last_action.get('impact_score', 'N/A')}", True, (0, 0, 0))
        confidence = self.font.render(f"Confidence: {self.last_action.get('confidence', 'N/A')}", True, (0, 0, 0))
        
        self.screen.blit(action, (x + 40, y + 50))
        self.screen.blit(impact, (x + 40, y + 80))
        self.screen.blit(confidence, (x + 40, y + 110))
        
        # Controls instruction
        controls = self.font.render("Press D to add delay, R to reset, ESC to quit", True, (100, 100, 100))
        self.screen.blit(controls, (x + 20, y + 130))