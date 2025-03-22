import pygame
import math
from core.component import Component
from core.constants import *
from components.platform.data_source import DataSource
from components.platform.emul.rpm_emulator import RPMEmulator

class RPMGauge(Component):
    def __init__(self, region, port=RPM_PORT):
        """Initialize the RPM gauge component.
        
        Args:
            region (tuple): The (x, y, width, height) region for this component
            port (int): The port number for the data source connection
        """
        super().__init__(region, "RPM")
        self.rpm = 0
        self.max_rpm = 8000
        self.radius = min(self.width, self.height) // 2 - 40
        
        # Setup data source
        self.data_source = DataSource(port=port)
        self.data_source.set_data_callback(self._process_data)
        
        # For simulation
        self.simulating = False

        self.rpm_emulator = None

    def start_simulation(self):
        self.simulating = False
        self.rpm_emulator = RPMEmulator(port=RPM_PORT)
        self.rpm_emulator.start()
        self.connect()


    def _process_data(self, data):
        """Process received RPM data.
        
        Args:
            data (bytes): The received RPM data
        """
        try:
            self.rpm = int(data.decode())
        except Exception as e:
            print(f"RPM data processing error: {e}")
    
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
    
    def cleanup(self):
        self.simulating = False
        self.disconnect()
        self.rpm_emulator.stop()

    def draw(self, surface):
        """Draw the RPM gauge on the given surface.
        
        Args:
            surface (pygame.Surface): The surface to draw on
        """
        super().draw(surface)
        
        # Draw gauge background
        pygame.draw.circle(surface, CHARCOAL_1, 
                          (self.center_x, self.center_y), 
                          self.radius)
        
        # Draw ticks and labels
        font_small = pygame.font.SysFont('Arial', 14)
        for i in range(0, self.max_rpm + 1, 1000):
            angle = math.pi * 0.75 + (i / self.max_rpm) * math.pi * 1.5
            start_x = self.center_x + (self.radius - 15) * math.cos(angle)
            start_y = self.center_y + (self.radius - 15) * math.sin(angle)
            end_x = self.center_x + (self.radius - 5) * math.cos(angle)
            end_y = self.center_y + (self.radius - 5) * math.sin(angle)
            pygame.draw.line(surface, LIGHT_GREY_2, 
                            (int(start_x), int(start_y)), 
                            (int(end_x), int(end_y)), 
                            2)
            
            # Draw labels for every 2000 RPM
            if i % 2000 == 0:
                label_x = self.center_x + (self.radius - 35) * math.cos(angle)
                label_y = self.center_y + (self.radius - 35) * math.sin(angle)
                label = font_small.render(f"{i//1000}", True, LIGHT_GREY_2)
                surface.blit(label, (int(label_x - 10), int(label_y - 10)))
        
        # Draw redline area (7000+ RPM)
        redline_start_angle = math.pi * 0.75 + (7000 / self.max_rpm) * math.pi * 1.5
        redline_end_angle = math.pi * 0.75 + math.pi * 1.5
        arc_points = []
        
        # Generate points for the redline arc
        for angle in range(int(redline_start_angle * 180 / math.pi), 
                           int(redline_end_angle * 180 / math.pi), 
                           2):
            rad = angle * math.pi / 180
            x = self.center_x + (self.radius - 10) * math.cos(rad)
            y = self.center_y + (self.radius - 10) * math.sin(rad)
            arc_points.append((x, y))
            
            x_inner = self.center_x + (self.radius - 20) * math.cos(rad)
            y_inner = self.center_y + (self.radius - 20) * math.sin(rad)
            arc_points.insert(0, (x_inner, y_inner))
        
        # Draw redline area if we have enough points
        if len(arc_points) >= 3:
            pygame.draw.polygon(surface, (200, 0, 0, 100), arc_points)
        
        # Draw needle
        angle = math.pi * 0.75 + (self.rpm / self.max_rpm) * math.pi * 1.5
        needle_x = self.center_x + (self.radius - 20) * math.cos(angle)
        needle_y = self.center_y + (self.radius - 20) * math.sin(angle)
        
        # Needle color: green to yellow to red based on RPM
        if self.rpm < 5000:
            needle_color = (0, 255, 0)  # Green
        elif self.rpm < 7000:
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
        
        # Draw RPM text
        font = pygame.font.SysFont('Arial', 24, bold=True)
        text = font.render(f"{self.rpm} RPM", True, WHITE)
        text_rect = text.get_rect(center=(self.center_x, self.center_y + 50))
        surface.blit(text, text_rect)
        
        # Draw "RPM x1000" label
        label = font_small.render("RPM x1000", True, LIGHT_GREY_2)
        label_rect = label.get_rect(center=(self.center_x, self.y + self.height - 30))
        surface.blit(label, label_rect)