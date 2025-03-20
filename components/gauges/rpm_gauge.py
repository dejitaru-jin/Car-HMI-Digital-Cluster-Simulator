import pygame
import math
import random
from core.component import Component

class RPMGauge(Component):
    def __init__(self, region):
        super().__init__(region, "RPM")
        self.rpm = 0
        self.max_rpm = 8000
        self.radius = min(self.width, self.height) // 2 - 40
        
        # For simulation
        self.simulating = False
        
    def _process_data(self, data):
        try:
            self.rpm = int(data.decode())
        except Exception as e:
            print(f"RPM data processing error: {e}")
    
    def start_simulation(self):
        self.simulating = True
        
    def update(self):
        if self.simulating:
            # Simple simulation: RPM increases/decreases like an engine
            if random.random() < 0.5:
                self.rpm += random.randint(50, 200)
            else:
                self.rpm -= random.randint(50, 150)
            
            # Keep within bounds
            self.rpm = max(800, min(self.rpm, self.max_rpm))
    
    def draw(self, surface):
        super().draw(surface)
        
        # Draw gauge background
        pygame.draw.circle(surface, (40, 40, 50), 
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
            pygame.draw.line(surface, (200, 200, 200), 
                            (int(start_x), int(start_y)), 
                            (int(end_x), int(end_y)), 
                            2)
            
            # Draw labels for every 2000 RPM
            if i % 2000 == 0:
                label_x = self.center_x + (self.radius - 35) * math.cos(angle)
                label_y = self.center_y + (self.radius - 35) * math.sin(angle)
                label = font_small.render(f"{i//1000}", True, (200, 200, 200))
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
        text = font.render(f"{self.rpm} RPM", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.center_x, self.center_y + 50))
        surface.blit(text, text_rect)
        
        # Draw "RPM x1000" label
        label = font_small.render("RPM x1000", True, (200, 200, 200))
        label_rect = label.get_rect(center=(self.center_x, self.y + self.height - 30))
        surface.blit(label, label_rect)