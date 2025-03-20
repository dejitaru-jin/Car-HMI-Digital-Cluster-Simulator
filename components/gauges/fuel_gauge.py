import pygame
import math
from core.component import Component

class FuelGauge(Component):
    def __init__(self, region):
        super().__init__(region, "Fuel")
        self.fuel_level = 100  # Percentage
        self.radius = min(self.width, self.height) // 2 - 40
        
        # For simulation
        self.simulating = False
        
    def _process_data(self, data):
        try:
            self.fuel_level = float(data.decode())
        except Exception as e:
            print(f"Fuel data processing error: {e}")
    
    def start_simulation(self):
        self.simulating = True
        
    def update(self):
        if self.simulating:
            # Slowly decrease fuel level
            self.fuel_level -= 0.02
            if self.fuel_level < 0:
                self.fuel_level = 100
    
    def draw(self, surface):
        super().draw(surface)
        
        # Draw gauge background - smaller size than RPM/Speed
        pygame.draw.circle(surface, (40, 40, 50), 
                          (self.center_x, self.center_y), 
                          self.radius)
        
        # Draw fuel gauge - this is a half-circle gauge
        start_angle = math.pi * 0.75  # Start at 135 degrees
        end_angle = math.pi * 2.25    # End at 405 degrees (45 degrees)
        
        # Draw ticks and labels
        font_small = pygame.font.SysFont('Arial', 14)
        for pct in range(0, 101, 10):
            angle = start_angle + (pct / 100) * (end_angle - start_angle)
            start_x = self.center_x + (self.radius - 15) * math.cos(angle)
            start_y = self.center_y + (self.radius - 15) * math.sin(angle)
            end_x = self.center_x + (self.radius - 5) * math.cos(angle)
            end_y = self.center_y + (self.radius - 5) * math.sin(angle)
            pygame.draw.line(surface, (200, 200, 200), 
                            (int(start_x), int(start_y)), 
                            (int(end_x), int(end_y)), 
                            2)
            
            # Draw labels for Empty, 1/2, Full
            if pct in [0, 50, 100]:
                label_x = self.center_x + (self.radius - 35) * math.cos(angle)
                label_y = self.center_y + (self.radius - 35) * math.sin(angle)
                
                if pct == 0:
                    label_text = "E"
                elif pct == 50:
                    label_text = "1/2"
                else:
                    label_text = "F"
                    
                label = font_small.render(label_text, True, (200, 200, 200))
                surface.blit(label, (int(label_x - 10), int(label_y - 10)))
        
        # Draw the "danger zone" for low fuel
        danger_start_angle = start_angle
        danger_end_angle = start_angle + 0.15 * (end_angle - start_angle)
        arc_points = []
        
        # Generate points for the danger arc
        for angle in range(int(danger_start_angle * 180 / math.pi), 
                           int(danger_end_angle * 180 / math.pi), 
                           2):
            rad = angle * math.pi / 180
            x = self.center_x + (self.radius - 10) * math.cos(rad)
            y = self.center_y + (self.radius - 10) * math.sin(rad)
            arc_points.append((x, y))
            
            x_inner = self.center_x + (self.radius - 20) * math.cos(rad)
            y_inner = self.center_y + (self.radius - 20) * math.sin(rad)
            arc_points.insert(0, (x_inner, y_inner))
        
        # Draw danger area if we have enough points
        if len(arc_points) >= 3:
            pygame.draw.polygon(surface, (200, 0, 0, 100), arc_points)
        
        # Draw needle
        angle = start_angle + (self.fuel_level / 100) * (end_angle - start_angle)
        needle_x = self.center_x + (self.radius - 20) * math.cos(angle)
        needle_y = self.center_y + (self.radius - 20) * math.sin(angle)
        
        # Needle color: red if low fuel, otherwise white
        if self.fuel_level < 15:
            needle_color = (255, 0, 0)  # Red for low fuel
        else:
            needle_color = (255, 255, 255)  # White for normal
            
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
        text = font.render(f"{int(self.fuel_level)}%", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.center_x, self.center_y + 50))
        surface.blit(text, text_rect)
        
        # Draw fuel tank icon
        tank_width = 40
        tank_height = 20
        tank_x = self.center_x - tank_width // 2
        tank_y = self.center_y + 80
        
        # Draw tank outline
        pygame.draw.rect(surface, (200, 200, 200), 
                        (tank_x, tank_y, tank_width, tank_height), 
                        2)
        
        # Draw fuel cap
        pygame.draw.circle(surface, (200, 200, 200), 
                          (tank_x + tank_width + 5, tank_y + tank_height // 2), 
                          5, 1)