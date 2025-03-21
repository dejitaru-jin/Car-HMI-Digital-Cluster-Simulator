import pygame
import json
import time
from core.component import Component
from components.platform.data_source import DataSource

class MessagesWidget(Component):
    def __init__(self, region, port=5006):
        """Initialize the messages widget component.
        
        Args:
            region (tuple): The (x, y, width, height) region for this component
            port (int): The port number for the data source connection
        """
        super().__init__(region, "Messages")
        
        # Initialize messages data
        self.messages = []
        self.count = {"total": 0, "info": 0, "warning": 0, "critical": 0}
        self.max_visible_messages = 5
        self.last_update_time = 0
        
        # Message styling
        self.category_colors = {
            "info": (100, 200, 255),      # Blue
            "warning": (255, 180, 50),    # Orange
            "critical": (255, 50, 50)     # Red
        }
        
        # Setup data source
        self.data_source = DataSource(port=port)
        self.data_source.set_data_callback(self._process_data)
    
    def _process_data(self, data):
        """Process received messages data.
        
        Args:
            data (bytes): The received messages data
        """
        try:
            messages_data = json.loads(data.decode())
            self.messages = messages_data.get("messages", [])
            self.count = messages_data.get("count", {"total": 0, "info": 0, "warning": 0, "critical": 0})
            self.last_update_time = messages_data.get("timestamp", time.time())
        except Exception as e:
            print(f"Messages data processing error: {e}")
    
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
    
    def acknowledge_message(self, message_id):
        """Acknowledge a message.
        
        Args:
            message_id (int): ID of message to acknowledge
        """
        # This would send a command back to the emulator
        pass
    
    def dismiss_message(self, message_id):
        """Dismiss a message.
        
        Args:
            message_id (int): ID of message to dismiss
        """
        # This would send a command back to the emulator
        pass
    
    def draw(self, surface):
        """Draw the messages widget on the given surface.
        
        Args:
            surface (pygame.Surface): The surface to draw on
        """
        super().draw(surface)
        
        # Background
        background_rect = pygame.Rect(10, 10, self.width - 20, self.height - 20)
        pygame.draw.rect(surface, (40, 40, 50), background_rect, border_radius=10)
        
        # Header
        header_font = pygame.font.SysFont('Arial', 22, bold=True)
        header_text = header_font.render("Notifications", True, (240, 240, 255))
        surface.blit(header_text, (25, 20))
        
        # Count indicators
        count_y = 22
        count_font = pygame.font.SysFont('Arial', 14)
        
        # Total count
        total_count_text = count_font.render(f"Total: {self.count['total']}", 
                                           True, (220, 220, 230))
        surface.blit(total_count_text, (self.width - 100, count_y))
        
        # Category counts
        category_spacing = 25
        for i, category in enumerate(["info", "warning", "critical"]):
            count = self.count.get(category, 0)
            if count > 0:
                count_color = self.category_colors[category]
            else:
                count_color = (150, 150, 160)
                
            category_count_text = count_font.render(
                f"{category.capitalize()}: {count}", 
                True, 
                count_color
            )
            surface.blit(category_count_text, 
                         (25, 50 + i * category_spacing))
        
        # Messages area
        messages_area_rect = pygame.Rect(15, 110, self.width - 30, self.height - 130)
        pygame.draw.rect(surface, (30, 30, 40), messages_area_rect, border_radius=5)
        
        # Message list
        if not self.messages:
            # No messages
            no_messages_font = pygame.font.SysFont('Arial', 18)
            no_messages_text = no_messages_font.render(
                "No notifications", 
                True, 
                (150, 150, 160)
            )
            no_messages_rect = no_messages_text.get_rect(
                center=(self.center_x, self.center_y)
            )
            surface.blit(no_messages_text, no_messages_rect)
        else:
            # Display messages
            self._draw_messages(surface, messages_area_rect)
    
    def _draw_messages(self, surface, container_rect):
        """Draw the list of messages.
        
        Args:
            surface (pygame.Surface): The surface to draw on
            container_rect (pygame.Rect): The container rectangle
        """
        # Sort messages: critical first, then warning, then info, newest first within each category
        sorted_messages = sorted(
            self.messages, 
            key=lambda m: (
                0 if m["category"] == "critical" else 
                1 if m["category"] == "warning" else 2,
                -m["timestamp"]  # Negative for descending order
            )
        )
        
        # Limit to max visible
        visible_messages = sorted_messages[:self.max_visible_messages]
        
        # Message styling
        message_font = pygame.font.SysFont('Arial', 16)
        timestamp_font = pygame.font.SysFont('Arial', 12)
        message_height = 45
        message_spacing = 5
        message_width = container_rect.width - 10
        
        # Draw each message
        for i, message in enumerate(visible_messages):
            # Message background
            y_pos = container_rect.y + 5 + i * (message_height + message_spacing)
            message_rect = pygame.Rect(
                container_rect.x + 5, 
                y_pos, 
                message_width, 
                message_height
            )
            
            # Background color based on category and acknowledgement
            if message["acknowledged"]:
                # Dimmed if acknowledged
                bg_color = (50, 50, 60)
            else:
                # Category-based color
                category = message["category"]
                r, g, b = self.category_colors.get(category, (100, 100, 120))
                bg_color = (int(r * 0.3), int(g * 0.3), int(b * 0.3))
            
            pygame.draw.rect(surface, bg_color, message_rect, border_radius=3)
            
            # Category indicator
            indicator_width = 5
            indicator_rect = pygame.Rect(
                message_rect.x, 
                message_rect.y, 
                indicator_width, 
                message_rect.height
            )
            pygame.draw.rect(
                surface, 
                self.category_colors.get(message["category"], (100, 100, 120)),
                indicator_rect, 
                border_radius=3
            )
            
            # Message content
            content_text = message_font.render(
                self._truncate_text(message["content"], 40), 
                True, 
                (220, 220, 230)
            )
            surface.blit(content_text, (message_rect.x + 10, message_rect.y + 5))
            
            # Timestamp
            timestamp = message["timestamp"]
            current_time = time.time()
            time_diff = current_time - timestamp
            
            if time_diff < 60:
                # Less than a minute
                time_str = "Just now"
            elif time_diff < 3600:
                # Less than an hour
                minutes = int(time_diff / 60)
                time_str = f"{minutes}m ago"
            else:
                # More than an hour
                hours = int(time_diff / 3600)
                time_str = f"{hours}h ago"
                
            timestamp_text = timestamp_font.render(
                time_str, 
                True, 
                (180, 180, 190)
            )
            surface.blit(
                timestamp_text, 
                (message_rect.x + 10, message_rect.y + 25)
            )
        
        # Indicate if there are more messages
        if len(sorted_messages) > self.max_visible_messages:
            more_font = pygame.font.SysFont('Arial', 14)
            more_text = more_font.render(
                f"+{len(sorted_messages) - self.max_visible_messages} more notifications", 
                True, 
                (180, 180, 190)
            )
            more_rect = more_text.get_rect(
                center=(
                    container_rect.x + container_rect.width // 2,
                    container_rect.y + container_rect.height - 20
                )
            )
            surface.blit(more_text, more_rect)
    
    def _truncate_text(self, text, max_chars):
        """Truncate text to maximum character length.
        
        Args:
            text (str): Text to truncate
            max_chars (int): Maximum characters
            
        Returns:
            str: Truncated text
        """
        if len(text) > max_chars:
            return text[:max_chars - 3] + "..."
        return text