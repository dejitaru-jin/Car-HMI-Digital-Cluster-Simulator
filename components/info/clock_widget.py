import pygame
import math
import json
from datetime import datetime
from core.component import Component
from components.platform.data_source import DataSource

class ClockWidget(Component):
    def __init__(self, region, port=5004):
        """Initialize the clock widget component.
        
        Args:
            region (tuple): The (x, y, width, height) region for this component
            port (int): The port number for the data source connection
        """
        super().__init__(region, "Clock")
        
        # Initialize clock data
        self.hour = 0
        self.minute = 0
        self.second = 0
        self.time_str = "00:00"
        self.date_str = ""
        
        # Clock display settings
        self.show_analog = True
        self.show_digital = True
        self.show_date = True
        self.radius = min(self.width, self.height) // 2 - 40
        
        # Setup data source
        self.data_source = DataSource(port=port)
        self.data_source.set_data_callback(self._process_data)
    
    def _process_data(self, data):
        """Process received clock data.
        
        Args:
            data (bytes): The received clock data
        """
        try:
            clock_data = json.loads(data.decode())
            self.time_str = clock_data.get("time", "00:00")
            self.date_str = clock_data.get("date", "")
            self.hour = clock_data.get("hour", 0)
            self.minute = clock_data.get("minute", 0)
            self.second = clock_data.get("second", 0)
        except Exception as e:
            print(f"Clock data processing error: {e}")
    
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
    
    def toggle_analog(self):
        """Toggle the analog clock display."""
        self.show_analog = not self.show_analog
    
    def toggle_digital(self):
        """Toggle the digital clock display."""
        self.show_digital = not self.show_digital
    
    def toggle_date(self):
        """Toggle the date display."""
        self.show_date = not self.show_date
    
    def draw(self, surface):
        """Draw the clock widget on the given surface.
        
        Args:
            surface (pygame.Surface): The surface to draw on
        """
        super().draw(surface)
        
        # If both analog and digital are hidden, show at least digital
        if not self.show_analog and not self.show_digital:
            self.show_digital = True
        
        # Draw analog clock
        if self.show_analog:
            self._draw_analog_clock(surface)
        
        # Draw digital clock
        if self.show_digital:
            self._draw_digital_clock(surface)
        
        # Draw date
        if self.show_date and self.date_str:
            self._draw_date(surface)
    
    def _draw_analog_clock(self, surface):
        """Draw the analog clock face.
        
        Args:
            surface (pygame.Surface): The surface to draw on
        """
        # Clock position and size
        if self.show_digital:
            # Smaller clock if showing digital too
            clock_y = self.center_y - 20
            radius = min(self.radius, 60)
        else:
            # Larger clock if only analog
            clock_y = self.center_y
            radius = self.radius
            
        # Draw clock face
        pygame.draw.circle(surface, (50, 50, 60), 
                          (self.center_x, clock_y), 
                          radius)
        pygame.draw.circle(surface, (210, 210, 220), 
                          (self.center_x, clock_y), 
                          radius, 2)
        
        # Draw hour ticks
        for i in range(12):
            angle = math.pi / 6 * i - math.pi / 2
            start_x = self.center_x + (radius - 10) * math.cos(angle)
            start_y = clock_y + (radius - 10) * math.sin(angle)
            end_x = self.center_x + radius * math.cos(angle)
            end_y = clock_y + radius * math.sin(angle)
            pygame.draw.line(surface, (240, 240, 250), 
                            (int(start_x), int(start_y)), 
                            (int(end_x), int(end_y)), 
                            2)
        
        # Draw hands
        # Hour hand
        hour_angle = (self.hour % 12 + self.minute / 60) * math.pi / 6 - math.pi / 2
        hour_x = self.center_x + radius * 0.5 * math.cos(hour_angle)
        hour_y = clock_y + radius * 0.5 * math.sin(hour_angle)
        pygame.draw.line(surface, (255, 255, 255), 
                        (self.center_x, clock_y), 
                        (int(hour_x), int(hour_y)), 
                        4)
        
        # Minute hand
        minute_angle = (self.minute + self.second / 60) * math.pi / 30 - math.pi / 2
        minute_x = self.center_x + radius * 0.7 * math.cos(minute_angle)
        minute_y = clock_y + radius * 0.7 * math.sin(minute_angle)
        pygame.draw.line(surface, (255, 255, 255), 
                        (self.center_x, clock_y), 
                        (int(minute_x), int(minute_y)), 
                        2)
        
        # Second hand (if clock is large enough)
        if radius > 40:
            second_angle = self.second * math.pi / 30 - math.pi / 2
            second_x = self.center_x + radius * 0.8 * math.cos(second_angle)
            second_y = clock_y + radius * 0.8 * math.sin(second_angle)
            pygame.draw.line(surface, (255, 0, 0), 
                            (self.center_x, clock_y), 
                            (int(second_x), int(second_y)), 
                            1)
        
        # Draw center dot
        pygame.draw.circle(surface, (230, 230, 240), 
                          (self.center_x, clock_y), 
                          4)
    
    def _draw_digital_clock(self, surface):
        """Draw the digital clock.
        
        Args:
            surface (pygame.Surface): The surface to draw on
        """
        font = pygame.font.SysFont('Arial', 26, bold=True)
        
        # Position depends on whether we're showing analog clock
        if self.show_analog:
            text_y = self.center_y + 40
        else:
            text_y = self.center_y - 15
            
        # Draw digital time
        text = font.render(self.time_str, True, (240, 240, 255))
        text_rect = text.get_rect(center=(self.center_x, text_y))
        surface.blit(text, text_rect)
    
    def _draw_date(self, surface):
        """Draw the date.
        
        Args:
            surface (pygame.Surface): The surface to draw on
        """
        font = pygame.font.SysFont('Arial', 18)
        
        # Position depends on what else is visible
        if self.show_analog and self.show_digital:
            text_y = self.center_y + 75
        elif self.show_digital:
            text_y = self.center_y + 20
        else:  # Only analog
            text_y = self.center_y + 50
            
        # Draw date text
        text = font.render(self.date_str, True, (200, 200, 210))
        text_rect = text.get_rect(center=(self.center_x, text_y))
        surface.blit(text, text_rect)