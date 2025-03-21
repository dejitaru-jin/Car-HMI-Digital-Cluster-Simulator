import pygame
import math
import random
from core.component import Component

class SpeedGauge(Component):
    def __init__(self, region):
        super().__init__(region, "Speed")
        self.speed = 0
        self.max_speed = 240
        self.radius = min(self.width, self.height) // 2 - 40
        
        # For simulation
        self.simulating = False
        self.target_speed = 0
        
    def _process_data(self, data):
        try:
            self.speed = float(data.decode())
        except Exception as e:
            print(f"Speed data processing error: {e}")
    
    def start_simulation(self):
        self.simulating = True
        
    def update(self):
        if self.simulating:
            # Every 10 seconds, set a new target speed
            if random.random() < 0.01:
                self.target_speed = random.randint(0, self.max_speed)
            
            # Move current speed toward target
            if self.speed < self.target_speed:
                self.speed += min(2.0, self.target_speed - self.speed)
            elif self.speed > self.target_speed:
                self.speed -= min(1.5, self.speed - self.target_speed)

    def cleanup(self):
        self.simulating = False
    
    def draw(self, surface):
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
                label = font_small.render(f"{i}", True, (200, 200, 200))
                surface.blit(label, (int(label_x - 10), int(label_y - 10)))
        
        # Draw needle
        angle = math.pi * 0.75 + (self.speed / self.max_speed) * math.pi * 1.5
        needle_x = self.center_x + (self.radius - 20) * math.cos(angle)
        needle_y = self.center_y + (self.radius - 20) * math.sin(angle)
        
        pygame.draw.line(surface, (0, 200, 255), 
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