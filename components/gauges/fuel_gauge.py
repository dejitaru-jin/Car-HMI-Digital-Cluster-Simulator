import pygame
import math
from core.component import Component
from components.platform.data_source import DataSource

class FuelGauge(Component):
    def __init__(self, region, port=5003):
        """Initialize the fuel gauge component.
        
        Args:
            region (tuple): The (x, y, width, height) region for this component
            port (int): The port number for the data source connection
        """
        super().__init__(region, "Fuel")
        self.fuel_level = 100.0  # Percentage
        self.tank_capacity = 60.0  # Liters
        self.radius = min(self.width, self.height) // 2 - 40
        
        # Setup data source
        self.data_source = DataSource(port=port)
        self.data_source.set_data_callback(self._process_data)
    
    def _process_data(self, data):
        """Process received fuel data.
        
        Args:
            data (bytes): The received fuel data
        """
        try:
            self.fuel_level = float(data.decode())
        except Exception as e:
            print(f"Fuel data processing error: {e}")
    
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
        """Draw the fuel gauge on the given surface.
        
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
        # Fuel gauge only shows 0 to 1 (empty to full) over 3/4 of a circle
        for i in range(0, 101, 10):
            # Map 0-100 to the 3/4 circle from bottom left to bottom right
            angle = math.pi * 1.25 - (i / 100) * math.pi * 1.5
            start_x = self.center_x + (self.radius - 15) * math.cos(angle)
            start_y = self.center_y + (self.radius - 15) * math.sin(angle)
            end_x = self.center_x + (self.radius - 5) * math.cos(angle)
            end_y = self.center_y + (self.radius - 5) * math.sin(angle)
            pygame.draw.line(surface, (200, 200, 200), 
                            (int(start_x), int(start_y)), 
                            (int(end_x), int(end_y)), 
                            2)
            
            # Draw labels at empty, 1/2, and full
            if i in [0, 50, 100]:
                label_x = self.center_x + (self.radius - 35) * math.cos(angle)
                label_y = self.center_y + (self.radius - 35) * math.sin(angle)
                
                if i == 0:
                    label_text = "E"
                elif i == 50:
                    label_text = "1/2"
                else:
                    label_text = "F"
                    
                label = font_small.render(label_text, True, (200, 200, 200))
                label_rect = label.get_rect(center=(int(label_x), int(label_y)))
                surface.blit(label, label_rect)
        
        # Draw low fuel warning area (0-15%)
        low_fuel_start_angle = math.pi * 1.25
        low_fuel_end_angle = math.pi * 1.25 - (15 / 100) * math.pi * 1.5
        arc_points = []
        
        # Generate points for the low fuel arc
        for angle in range(int(low_fuel_start_angle * 180 / math.pi), 
                           int(low_fuel_end_angle * 180 / math.pi), 
                           -2):  # Negative step because angles decrease
            rad = angle * math.pi / 180
            x = self.center_x + (self.radius - 10) * math.cos(rad)
            y = self.center_y + (self.radius - 10) * math.sin(rad)
            arc_points.append((x, y))
            
            x_inner = self.center_x + (self.radius - 20) * math.cos(rad)
            y_inner = self.center_y + (self.radius - 20) * math.sin(rad)
            arc_points.append((x_inner, y_inner))
        
        # Draw low fuel area if we have enough points
        if len(arc_points) >= 3:
            pygame.draw.polygon(surface, (255, 0, 0, 100), arc_points)
        
        # Draw needle
        angle = math.pi * 1.25 - (self.fuel_level / 100) * math.pi * 1.5
        needle_x = self.center_x + (self.radius - 20) * math.cos(angle)
        needle_y = self.center_y + (self.radius - 20) * math.sin(angle)
        
        # Needle color: red if low fuel, otherwise green
        if self.fuel_level < 15:
            needle_color = (255, 0, 0)  # Red for low fuel
        else:
            needle_color = (0, 255, 0)  # Green otherwise
            
        pygame.draw.line(surface, needle_color, 
                        (self.center_x, self.center_y), 
                        (int(needle_x), int(needle_y)), 
                        3)
        
        # Draw center cap
        pygame.draw.circle(surface, (100, 100, 100), 
                          (self.center_x, self.center_y), 
                          10)
        
        # Draw fuel level text
        font = pygame.font.SysFont('Arial', 24, bold=True)
        
        # Calculate liters remaining
        liters = (self.fuel_level / 100) * self.tank_capacity
        
        # Show percentage and liters
        text = font.render(f"{int(self.fuel_level)}% ({int(liters)}L)", True, 
                          (255, 0, 0) if self.fuel_level < 15 else (255, 255, 255))
        text_rect = text.get_rect(center=(self.center_x, self.center_y + 50))
        surface.blit(text, text_rect)
        
        # Draw fuel symbol
        fuel_icon_x = self.center_x - 25
        fuel_icon_y = self.center_y + 80
        
        # Draw pump handle
        pygame.draw.rect(surface, (200, 200, 200), 
                        (fuel_icon_x, fuel_icon_y, 10, 15))
        pygame.draw.rect(surface, (200, 200, 200), 
                        (fuel_icon_x + 10, fuel_icon_y + 5, 15, 5))
        
        # Draw pump body
        pygame.draw.rect(surface, (200, 200, 200), 
                        (fuel_icon_x + 25, fuel_icon_y - 5, 20, 25))
        
        # Fuel label
        label = font_small.render("FUEL", True, (200, 200, 200))
        label_rect = label.get_rect(center=(self.center_x + 25, self.center_y + 80))
        surface.blit(label, label_rect)