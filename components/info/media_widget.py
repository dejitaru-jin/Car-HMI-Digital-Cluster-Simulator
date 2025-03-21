import pygame
import random
from core.component import Component

class MediaInfoWidget(Component):
    def __init__(self, region):
        super().__init__(region, "Media")
        self.track_title = "No Track"
        self.artist = "No Artist"
        self.album = "No Album"
        self.duration = 0  # seconds
        self.position = 0  # seconds
        self.is_playing = False
        
        # For simulation
        self.simulating = False
        self.songs = [
            {"title": "Bohemian Rhapsody", "artist": "Queen", "album": "A Night at the Opera", "duration": 355},
            {"title": "Imagine", "artist": "John Lennon", "album": "Imagine", "duration": 183},
            {"title": "Sweet Child O' Mine", "artist": "Guns N' Roses", "album": "Appetite for Destruction", "duration": 355},
            {"title": "Billie Jean", "artist": "Michael Jackson", "album": "Thriller", "duration": 294},
            {"title": "Smells Like Teen Spirit", "artist": "Nirvana", "album": "Nevermind", "duration": 301},
        ]
        self.current_song_index = 0
        
    def _process_data(self, data):
        try:
            media_info = data.decode().split('|')
            if len(media_info) >= 5:
                self.track_title = media_info[0]
                self.artist = media_info[1]
                self.album = media_info[2]
                self.duration = int(media_info[3])
                self.position = int(media_info[4])
                self.is_playing = media_info[5].lower() == 'true' if len(media_info) > 5 else False
        except Exception as e:
            print(f"Media data processing error: {e}")
    
    def start_simulation(self):
        self.simulating = True
        self._load_current_song()
        self.is_playing = True
        
    def _load_current_song(self):
        song = self.songs[self.current_song_index]
        self.track_title = song["title"]
        self.artist = song["artist"]
        self.album = song["album"]
        self.duration = song["duration"]
        self.position = 0

    def cleanup(self):
        self.simulating = False
            
    def update(self):
        if self.simulating and self.is_playing:
            # Update position
            self.position += 1
            
            # Change song when finished
            if self.position >= self.duration:
                self.current_song_index = (self.current_song_index + 1) % len(self.songs)
                self._load_current_song()
                
            # Randomly pause or play
            if random.random() < 0.001:
                self.is_playing = not self.is_playing
    
    def draw(self, surface):
        super().draw(surface)
        
        # Draw media player
        player_width = self.width - 40
        player_height = self.height - 80
        player_x = 20
        player_y = 40
        
        # Background
        pygame.draw.rect(surface, (30, 30, 40), 
                        (player_x, player_y, player_width, player_height))
        pygame.draw.rect(surface, (70, 70, 90), 
                        (player_x, player_y, player_width, player_height), 
                        1)
        
        # Track information
        font_title = pygame.font.SysFont('Arial', 22, bold=True)
        font_info = pygame.font.SysFont('Arial', 18)
        
        # Title
        title_text = font_title.render(self.track_title, True, (230, 230, 255))
        title_rect = title_text.get_rect(midtop=(self.center_x, player_y + 20))
        surface.blit(title_text, title_rect)
        
        # Artist & Album
        artist_text = font_info.render(f"{self.artist} - {self.album}", True, (200, 200, 220))
        artist_rect = artist_text.get_rect(midtop=(self.center_x, player_y + 50))
        surface.blit(artist_text, artist_rect)
        
        # Progress bar
        progress_width = player_width - 40
        progress_height = 10
        progress_x = player_x + 20
        progress_y = player_y + 90
        
        # Background track
        pygame.draw.rect(surface, (50, 50, 60), 
                        (progress_x, progress_y, progress_width, progress_height))
        
        # Progress fill
        if self.duration > 0:
            fill_width = int((self.position / self.duration) * progress_width)
            pygame.draw.rect(surface, (100, 100, 255), 
                            (progress_x, progress_y, fill_width, progress_height))
        
        # Time info
        position_min = self.position // 60
        position_sec = self.position % 60
        duration_min = self.duration // 60
        duration_sec = self.duration % 60
        
        time_text = font_info.render(f"{position_min:02d}:{position_sec:02d} / {duration_min:02d}:{duration_sec:02d}", 
                                   True, (200, 200, 220))
        time_rect = time_text.get_rect(midtop=(self.center_x, progress_y + 20))
        surface.blit(time_text, time_rect)
        
        # Control buttons
        button_y = progress_y + 50
        button_radius = 15
        spacing = 40
        
        # Previous button
        prev_x = self.center_x - spacing
        pygame.draw.circle(surface, (70, 70, 90), (prev_x, button_y), button_radius)
        pygame.draw.polygon(surface, (200, 200, 220), 
                          [(prev_x + 5, button_y), (prev_x - 5, button_y - 8), (prev_x - 5, button_y + 8)])
        pygame.draw.line(surface, (200, 200, 220), 
                        (prev_x - 6, button_y - 8), (prev_x - 6, button_y + 8), 2)
        
        # Play/Pause button
        play_x = self.center_x
        pygame.draw.circle(surface, (70, 70, 90), (play_x, button_y), button_radius)
        
        if self.is_playing:
            # Pause icon
            pygame.draw.line(surface, (200, 200, 220), 
                            (play_x - 4, button_y - 6), (play_x - 4, button_y + 6), 3)
            pygame.draw.line(surface, (200, 200, 220), 
                            (play_x + 4, button_y - 6), (play_x + 4, button_y + 6), 3)
        else:
            # Play icon
            pygame.draw.polygon(surface, (200, 200, 220), 
                              [(play_x - 5, button_y - 8), (play_x + 7, button_y), (play_x - 5, button_y + 8)])
        
        # Next button
        next_x = self.center_x + spacing
        pygame.draw.circle(surface, (70, 70, 90), (next_x, button_y), button_radius)
        pygame.draw.polygon(surface, (200, 200, 220), 
                          [(next_x - 5, button_y), (next_x + 5, button_y - 8), (next_x + 5, button_y + 8)])
        pygame.draw.line(surface, (200, 200, 220), 
                        (next_x + 6, button_y - 8), (next_x + 6, button_y + 8), 2)