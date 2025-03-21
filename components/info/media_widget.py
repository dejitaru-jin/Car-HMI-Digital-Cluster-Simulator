import pygame
import json
from core.component import Component
from components.platform.data_source import DataSource

class MediaInfoWidget(Component):
    def __init__(self, region, port=5005):
        """Initialize the media info widget component.
        
        Args:
            region (tuple): The (x, y, width, height) region for this component
            port (int): The port number for the data source connection
        """
        super().__init__(region, "Media")
        
        # Initialize media data
        self.title = "No track"
        self.artist = "No artist"
        self.album = "No album"
        self.duration = 0
        self.position = 0
        self.progress = 0
        self.playing = False
        self.repeat_mode = "off"
        self.shuffle_mode = False
        self.volume = 70
        
        # Setup data source
        self.data_source = DataSource(port=port)
        self.data_source.set_data_callback(self._process_data)
    
    def _process_data(self, data):
        """Process received media data.
        
        Args:
            data (bytes): The received media data
        """
        try:
            media_data = json.loads(data.decode())
            self.title = media_data.get("title", "No track")
            self.artist = media_data.get("artist", "No artist")
            self.album = media_data.get("album", "No album")
            self.duration = media_data.get("duration", 0)
            self.position = media_data.get("position", 0)
            self.progress = media_data.get("progress", 0)
            self.playing = media_data.get("playing", False)
            self.repeat_mode = media_data.get("repeat_mode", "off")
            self.shuffle_mode = media_data.get("shuffle_mode", False)
            self.volume = media_data.get("volume", 70)
        except Exception as e:
            print(f"Media data processing error: {e}")
    
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
        """Draw the media widget on the given surface.
        
        Args:
            surface (pygame.Surface): The surface to draw on
        """
        super().draw(surface)
        
        # Background
        background_rect = pygame.Rect(10, 10, self.width - 20, self.height - 20)
        pygame.draw.rect(surface, (40, 40, 50), background_rect, border_radius=10)
        
        # Media icon at top left
        icon_rect = pygame.Rect(25, 25, 30, 30)
        pygame.draw.rect(surface, (80, 80, 100), icon_rect, border_radius=5)
        
        # Draw music note icon
        note_x, note_y = 30, 30
        # Stem
        pygame.draw.line(surface, (200, 200, 220), 
                        (note_x + 15, note_y), 
                        (note_x + 15, note_y + 20), 
                        2)
        # Note head
        pygame.draw.ellipse(surface, (200, 200, 220), 
                           (note_x + 8, note_y + 17, 14, 10))
        
        # Media title
        title_font = pygame.font.SysFont('Arial', 22, bold=True)
        title_text = title_font.render(self._truncate_text(self.title, 18), 
                                     True, (240, 240, 255))
        surface.blit(title_text, (70, 25))
        
        # Artist and album
        info_font = pygame.font.SysFont('Arial', 16)
        artist_text = info_font.render(self._truncate_text(self.artist, 22), 
                                      True, (200, 200, 210))
        surface.blit(artist_text, (70, 50))
        
        album_text = info_font.render(self._truncate_text(f"Album: {self.album}", 25), 
                                     True, (180, 180, 190))
        surface.blit(album_text, (25, 80))
        
        # Progress bar
        progress_bar_rect = pygame.Rect(25, 110, self.width - 50, 15)
        pygame.draw.rect(surface, (60, 60, 70), progress_bar_rect, border_radius=3)
        
        # Fill progress bar based on current position
        if self.duration > 0:
            fill_width = int((self.progress / 100) * (self.width - 50))
            progress_fill_rect = pygame.Rect(25, 110, fill_width, 15)
            
            # Color based on playing status
            if self.playing:
                fill_color = (0, 120, 255)  # Blue when playing
            else:
                fill_color = (100, 100, 120)  # Gray when paused
                
            pygame.draw.rect(surface, fill_color, progress_fill_rect, border_radius=3)
        
        # Time display
        time_font = pygame.font.SysFont('Arial', 14)
        position_str = self._format_time(self.position)
        duration_str = self._format_time(self.duration)
        time_text = time_font.render(f"{position_str} / {duration_str}", 
                                   True, (190, 190, 200))
        time_rect = time_text.get_rect(center=(self.center_x, 135))
        surface.blit(time_text, time_rect)
        
        # Control buttons
        button_y = 160
        button_radius = 15
        
        # Previous button
        prev_x = self.center_x - 60
        pygame.draw.circle(surface, (70, 70, 80), (prev_x, button_y), button_radius)
        # Previous icon (double triangle)
        pygame.draw.polygon(surface, (220, 220, 230), 
                          [(prev_x - 5, button_y), 
                           (prev_x - 5, button_y - 8),
                           (prev_x - 12, button_y)])
        pygame.draw.polygon(surface, (220, 220, 230), 
                          [(prev_x + 5, button_y), 
                           (prev_x + 5, button_y - 8),
                           (prev_x - 2, button_y)])
        
        # Play/Pause button
        play_x = self.center_x
        pygame.draw.circle(surface, (70, 70, 80), (play_x, button_y), button_radius + 5)
        
        if self.playing:
            # Pause icon (two bars)
            pygame.draw.rect(surface, (220, 220, 230), 
                            (play_x - 7, button_y - 8, 5, 16))
            pygame.draw.rect(surface, (220, 220, 230), 
                            (play_x + 2, button_y - 8, 5, 16))
        else:
            # Play icon (triangle)
            pygame.draw.polygon(surface, (220, 220, 230), 
                              [(play_x - 5, button_y - 8), 
                               (play_x - 5, button_y + 8),
                               (play_x + 8, button_y)])
        
        # Next button
        next_x = self.center_x + 60
        pygame.draw.circle(surface, (70, 70, 80), (next_x, button_y), button_radius)
        # Next icon (double triangle)
        pygame.draw.polygon(surface, (220, 220, 230), 
                          [(next_x + 5, button_y), 
                           (next_x + 5, button_y - 8),
                           (next_x + 12, button_y)])
        pygame.draw.polygon(surface, (220, 220, 230), 
                          [(next_x - 5, button_y), 
                           (next_x - 5, button_y - 8),
                           (next_x + 2, button_y)])
        
        # Shuffle and repeat indicators
        indicator_y = 190
        indicator_font = pygame.font.SysFont('Arial', 14)
        
        # Shuffle
        shuffle_color = (0, 255, 0) if self.shuffle_mode else (150, 150, 160)
        shuffle_text = indicator_font.render("SHUFFLE", True, shuffle_color)
        surface.blit(shuffle_text, (self.center_x - 70, indicator_y))
        
        # Repeat
        if self.repeat_mode == "off":
            repeat_color = (150, 150, 160)
            repeat_text = "REPEAT"
        elif self.repeat_mode == "single":
            repeat_color = (0, 255, 0)
            repeat_text = "REPEAT ONE"
        else:  # repeat all
            repeat_color = (0, 255, 0)
            repeat_text = "REPEAT ALL"
            
        repeat_label = indicator_font.render(repeat_text, True, repeat_color)
        surface.blit(repeat_label, (self.center_x + 10, indicator_y))
        
        # Volume indicator
        volume_y = 220
        volume_width = 150
        volume_height = 8
        
        # Volume bar background
        volume_bg_rect = pygame.Rect(
            self.center_x - volume_width // 2, 
            volume_y, 
            volume_width, 
            volume_height
        )
        pygame.draw.rect(surface, (60, 60, 70), volume_bg_rect, border_radius=2)
        
        # Volume bar fill
        volume_fill_width = int((self.volume / 100) * volume_width)
        volume_fill_rect = pygame.Rect(
            self.center_x - volume_width // 2, 
            volume_y, 
            volume_fill_width, 
            volume_height
        )
        pygame.draw.rect(surface, (0, 180, 0), volume_fill_rect, border_radius=2)
        
        # Volume label
        volume_label = indicator_font.render(f"VOL: {self.volume}%", 
                                          True, (190, 190, 200))
        volume_label_rect = volume_label.get_rect(
            center=(self.center_x, volume_y + 20)
        )
        surface.blit(volume_label, volume_label_rect)
    
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
    
    def _format_time(self, seconds):
        """Format seconds as mm:ss string.
        
        Args:
            seconds (int): Time in seconds
            
        Returns:
            str: Formatted time string
        """
        minutes, seconds = divmod(int(seconds), 60)
        return f"{minutes}:{seconds:02}"