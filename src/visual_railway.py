import pygame
import numpy as np

class VisualRailway:
    def __init__(self, width=1000, height=600):
        self.width = width
        self.height = height
        self.tracks = self._create_track_network()
        self.stations = self._create_stations()
        
    def _create_track_network(self):
        """Create a realistic multi-track railway network"""
        return {
            'main_line': {
                'color': (0, 0, 0),  # Black - main line
                'points': [(100, 300), (300, 300), (500, 300), (700, 300), (900, 300)],
                'speed_limit': 100,
                'capacity': 2
            },
            'loop_line': {
                'color': (0, 100, 0),  # Green - loop line
                'points': [(100, 350), (250, 350), (400, 350), (550, 350), (700, 350), (900, 350)],
                'speed_limit': 80,
                'capacity': 1
            },
            'express_line': {
                'color': (100, 0, 0),  # Red - express line
                'points': [(100, 250), (400, 250), (700, 250), (900, 250)],
                'speed_limit': 120,
                'capacity': 1
            }
        }
    
    def _create_stations(self):
        """Create station positions"""
        return {
            'Delhi': (100, 280),
            'Ghaziabad': (300, 280),
            'Mathura': (500, 280),
            'Agra': (700, 280),
            'Mumbai': (900, 280)
        }
    
    def draw_network(self, screen):
        """Draw the complete railway network"""
        # Draw tracks
        for track_name, track_data in self.tracks.items():
            points = track_data['points']
            color = track_data['color']
            
            # Draw track line
            for i in range(len(points) - 1):
                pygame.draw.line(screen, color, points[i], points[i+1], 4)
            
            # Draw track label
            if points:
                font = pygame.font.Font(None, 20)
                label = font.render(track_name, True, color)
                screen.blit(label, (points[0][0], points[0][1] - 20))
        
        # Draw stations
        for station_name, pos in self.stations.items():
            pygame.draw.circle(screen, (0, 0, 200), pos, 8)
            font = pygame.font.Font(None, 18)
            label = font.render(station_name, True, (0, 0, 0))
            screen.blit(label, (pos[0] - 20, pos[1] + 15))
    
    def get_track_position(self, track_name, progress):
        """Get screen position along a track based on progress (0-1)"""
        track_points = self.tracks[track_name]['points']
        total_length = self._calculate_track_length(track_points)
        
        # Find which segment the train is on
        current_distance = progress * total_length
        accumulated = 0
        
        for i in range(len(track_points) - 1):
            segment_length = self._distance(track_points[i], track_points[i+1])
            if accumulated + segment_length >= current_distance:
                # Train is on this segment
                segment_progress = (current_distance - accumulated) / segment_length
                x = track_points[i][0] + (track_points[i+1][0] - track_points[i][0]) * segment_progress
                y = track_points[i][1] + (track_points[i+1][1] - track_points[i][1]) * segment_progress
                return (int(x), int(y))
            accumulated += segment_length
        
        return track_points[-1]  # End of track
    
    def _calculate_track_length(self, points):
        """Calculate total length of a track"""
        total = 0
        for i in range(len(points) - 1):
            total += self._distance(points[i], points[i+1])
        return total
    
    def _distance(self, point1, point2):
        """Calculate distance between two points"""
        return np.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)