import pygame
import random
from datetime import datetime
from core.component import Component

class MessagesWidget(Component):
    def __init__(self, region):
        super().__init__(region, "Messages")
        self.messages = []
        self.max_messages = 6
        
        # For simulation
        self.simulating = False
        self.simulation_messages = [
            {"text": "Low fuel warning", "priority": "high", "time": "08:15"},
            {"text": "Oil change reminder", "priority": "medium", "time": "09:30"},
            {"text": "Tire pressure optimal", "priority": "low", "time": "10:45"},
            {"text": "Navigation updated", "priority": "info", "time": "11:20"},
            {"text": "Scheduled service due", "priority": "medium", "time": "12:10"},
            {"text": "Car wash reminder", "priority": "low", "time": "13:05"},
            {"text": "Engine temperature high", "priority": "high", "time": "14:25"},
            {"text": "Brake pad wear detected", "priority": "high", "time": "15:40"},
            {"text": "Voice command activated", "priority": "info", "time": "16:15"},
        ]
        
    def _process_data(self, data):
        try:
            message_info = data.decode().split('|')
            if len(message_info) >= 3:
                message = {
                    "text": message_info[0],
                    "priority": message_info[1],
                    "time": message_info[2]
                }
                self.add_message(message)
        except Exception as e:
            print(f"Message data processing error: {e}")
    
    def add_message(self, message):
        self.messages.insert(0, message)  # Add to beginning
        if len(self.messages) > self.max_messages:
            self.messages.pop()  # Remove oldest
    
    def start_simulation(self):
        self.simulating = True
        
    def update(self):
        if self.simulating:
            # Add a random message every 5 seconds or so
            if random.random() < 0.005:
                msg = random.choice(self.simulation_messages)
                current_time = datetime.now().strftime("%H:%M")
                new_msg = msg.copy()
                new_msg["time"] = current_time
                self.add_message(new_msg)
    
    def draw(self, surface):
        super().draw(surface)
        
        # Draw message panel
        panel_width = self.width - 40
        panel_height = self.height - 80
        panel_x = 20
        panel_y = 40
        
        # Background
        pygame.draw.rect(surface, (30, 30, 40), 
                        (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(surface, (70, 70, 90), 
                        (panel_x, panel_y, panel_width, panel_height), 
                        1)
        
        # Header
        font_header = pygame.font.SysFont('Arial', 18, bold=True)
        header_text = font_header.render("Notifications", True, (200, 200, 220))
        header_rect = header_text.get_rect(midtop=(self.center_x, panel_y + 10))
        surface.blit(header_text, header_rect)
        
        # Messages
        font_message = pygame.font.SysFont('Arial', 16)
        font_time = pygame.font.SysFont('Arial', 14)
        
        message_y = panel_y + 40
        message_height = 30
        
        for i, message in enumerate(self.messages):
            # Message background with priority color
            if message["priority"] == "high":
                color = (200, 80, 80, 120)  # Red for high priority
            elif message["priority"] == "medium":
                color = (200, 200, 80, 120)  # Yellow for medium
            elif message["priority"] == "low":
                color = (80, 200, 80, 120)  # Green for low
            else:
                color = (80, 120, 200, 120)  # Blue for info
                
            pygame.draw.rect(surface, color, 
                            (panel_x + 10, message_y + i * message_height, 
                             panel_width - 20, message_height - 2))
            
            # Message text
            message_text = font_message.render(message["text"], True, (230, 230, 255))
            surface.blit(message_text, (panel_x + 20, message_y + i * message_height + 5))
            
            # Time
            time_text = font_time.render(message["time"], True, (180, 180, 200))
            time_rect = time_text.get_rect()
            time_rect.right = panel_x + panel_width - 20
            time_rect.centery = message_y + i * message_height + message_height // 2
            surface.blit(time_text, time_rect)