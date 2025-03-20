import pygame
import math
from datetime import datetime
from core.component import Component

class ClockWidget(Component):
    def __init__(self, region):
        super().__init__(region, "Clock")
        self.time = datetime.now()
        self.use_24h = True
        
        # For simulation
        self.simulating = False
        self.simulated_time = datetime.now()
        
    def _process_data(self, data):
        try:
            time_str = data.decode()
            self.time = datetime.strptime(time_str, "%H:%M:%S")
        except Exception as e:
            print(f"Clock data processing error: {e}")
    
    def start_simulation(self):
        self.simulating = True
        self.simulated_time = datetime.now()
        
    def update(self):
        if self.simulating:
            # Update time
            self.time = datetime.now()
        
    def draw(self, surface):
        super().draw(surface)
        
        # Draw analog clock
        radius = min(self.width, self.height) // 2 - 60
        
        # Draw clock face
        pygame.draw.circle(surface, (40, 40, 50), 
                          (self.center_x, self.center_y), 
                          radius)
        pygame.draw.circle(surface, (150, 150, 170), 
                          (self.center_x, self.center_y), 
                          radius, 
                          2)
        
        # Draw hour markers
        for i in range(12):
            angle = math.pi/6 * i - math.pi/2  # Start from 12 o'clock
            outer_x = self.center_x + radius * 0.9 * math.cos(angle)
            outer_y = self.center_y + radius * 0.9 * math.sin(angle)
            inner_x = self.center_x + radius * 0.8 * math.cos(angle)
            inner_y = self.center_y + radius * 0.8 * math.sin(angle)
            
            pygame.draw.line(surface, (200, 200, 220), 
                            (int(inner_x), int(inner_y)), 
                            (int(outer_x), int(outer_y)), 
                            3)
        
        # Get current time
        hour = self.time.hour % 12
        minute = self.time.minute
        second = self.time.second
        
        # Draw hour hand
        hour_angle = (hour + minute/60) * math.pi/6 - math.pi/2
        hour_x = self.center_x + radius * 0.5 * math.cos(hour_angle)
        hour_y = self.center_y + radius * 0.5 * math.sin(hour_angle)
        pygame.draw.line(surface, (200, 200, 255), 
                        (self.center_x, self.center_y), 
                        (int(hour_x), int(hour_y)), 
                        5)
        
        # Draw minute hand
        minute_angle = minute * math.pi/30 - math.pi/2
        minute_x = self.center_x + radius * 0.7 * math.cos(minute_angle)
        minute_y = self.center_y + radius * 0.7 * math.sin(minute_angle)
        pygame.draw.line(surface, (200, 200, 255), 
                        (self.center_x, self.center_y), 
                        (int(minute_x), int(minute_y)), 
                        3)
        
        # Draw second hand
        second_angle = second * math.pi/30 - math.pi/2
        second_x = self.center_x + radius * 0.8 * math.cos(second_angle)
        second_y = self.center_y + radius * 0.8 * math.sin(second_angle)
        pygame.draw.line(surface, (255, 100, 100), 
                        (self.center_x, self.center_y), 
                        (int(second_x), int(second_y)), 
                        1)
        
        # Draw center cap
        pygame.draw.circle(surface, (200, 200, 255), 
                          (self.center_x, self.center_y), 
                          8)
        
        # Draw digital time
        font = pygame.font.SysFont('Arial', 24, bold=True)
        
        if self.use_24h:
            time_str = self.time.strftime("%H:%M:%S")
        else:
            time_str = self.time.strftime("%I:%M:%S %p")
            
        text = font.render(time_str, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.center_x, self.center_y + radius + 30))
        surface.blit(text, text_rect)