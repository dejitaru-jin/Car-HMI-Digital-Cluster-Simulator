import pygame
import math
from core.component import Component
from components.platform.data_source import DataSource

class SpeedGauge(Component):
    def __init__(self, region, port=5002):
        """Initialize the speed gauge component.
        
        Args:
            region (tuple): The (x, y, width, height) region for this component
            port (int): The port number for the data source connection
        """
        super().__init__(region, "Speed")
        self.speed = 0
        self.max_speed = 220
        self.radius = min(self.width, self.height) // 2 - 40
        
        # Setup data source
        self.data_source = DataSource(port=port)
        self.data_source.set_data_callback(self._process_data)
    
    def _process_data(self, data):
        """Process received speed data.
        
        Args:
            data (bytes): The received speed data
        """
        try:
            self.speed = float(data.decode())
        except Exception as e:
            print(f"Speed data processing error: {e}")
    
    def connect(self):
        """Connect to the data source and start receiving data."""
        self.data_source.start()
    
    def disconnect(self):
        """Disconnect from the data source."""
        self.data_source.stop()
    
    def update(self):
        """Update the component state (called each frame)."""
        # Now handled by the data source
        pass
    
    def draw(self, surface):
        """Draw the speed gauge on the given surface.
        
        Args:
            surface (pygame.Surface): The surface to draw on
        """
        super().draw(surface)
        
        # Draw gauge background
        pygame.draw.circle(surface, (40, 40, 50), 
                          (self.center_x, self.center_y), 
                          self.radius)
        
        # Draw ticks and labels
        font_small = pygame.font.SysFont('Arial', 14)
        for i in range(0, self.max_speed + 1, 20):
            angle = math.pi * 0.75 + (i / self.max_speed) * math.pi * 1.5
            start_x = self.center_x + (self.radius - 15) * math.cos(angle)
            start_y = self.center_y + (self.radius - 15) * math.sin(angle)
            end_x = self.center_x + (self.radius - 5) * math.cos(angle)
            end_y = self.center_y + (self.radius - 5) * math.sin(angle)
            pygame.draw.line(surface, (200, 200, 200), 
                            (int(start_x), int(start_y)), 
                            (int(end_x), int(end_y)), 
                            2)
            
            # Draw labels for every 40 km/h
            if i % 40 == 0:
                label_x = self.center_x + (self.radius - 35) * math.cos(angle)
                label_y = self.center_y + (self.radius - 35) * math.sin(angle)
                label = font_small.render(str(i), True, (200, 200, 200))
                surface.blit(label, (int(label_x - 10), int(label_y - 10)))
        
        # Draw high-speed area (180+ km/h)
        high_speed_start_angle = math.pi * 0.75 + (180 / self.max_speed) * math.pi * 1.5
        high_speed_end_angle = math.pi * 0.75 + math.pi * 1.5
        arc_points = []
        
        # Generate points for the high-speed arc
        for angle in range(int(high_speed_start_angle * 180 / math.pi), 
                           int(high_speed_end_angle * 180 / math.pi), 
                           2):
            rad = angle * math.pi / 180
            x = self.center_x + (self.radius - 10) * math.cos(rad)
            y = self.center_y + (self.radius - 10) * math.sin(rad)
            arc_points.append((x, y))
            
            x_inner = self.center_x + (self.radius - 20) * math.cos(rad)
            y_inner = self.center_y + (self.radius - 20) * math.sin(rad)
            arc_points.insert(0, (x_inner, y_inner))
        
        # Draw high-speed area if we have enough points
        if len(arc_points) >= 3:
            pygame.draw.polygon(surface, (255, 165, 0, 100), arc_points)
        
        # Draw needle
        angle = math.pi * 0.75 + (self.speed / self.max_speed) * math.pi * 1.5
        needle_x = self.center_x + (self.radius - 20) * math.cos(angle)
        needle_y = self.center_y + (self.radius - 20) * math.sin(angle)
        
        # Needle color: green to yellow to red based on speed
        if self.speed < 100:
            needle_color = (0, 255, 0)  # Green
        elif self.speed < 180:
            needle_color = (255, 255, 0)  # Yellow
        else:
            needle_color = (255, 0, 0)  # Red
            
        pygame.draw.line(surface, needle_color, 
                        (self.center_x, self.center_y), 
                        (int(needle_x), int(needle_y)), 
                        3)
        
        # Draw center cap
        pygame.draw.circle(surface, (100, 100, 100), 
                          (self.center_x, self.center_y), 
                          10)
        
        # Draw speed text
        font = pygame.font.SysFont('Arial', 24, bold=True)
        text = font.render(f"{int(self.speed)} km/h", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.center_x, self.center_y + 50))
        surface.blit(text, text_rect)
        
        # Draw "SPEED" label
        label = font_small.render("SPEED", True, (200, 200, 200))
        label_rect = label.get_rect(center=(self.center_x, self.y + self.height - 30))
        surface.blit(label, label_rect)