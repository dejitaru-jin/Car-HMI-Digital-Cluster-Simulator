import pygame
import sys
import math
import time
import threading
import socket
import random
from datetime import datetime

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
BG_COLOR = (20, 20, 30)  # Dark blue-gray background

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Car HMI Emulator")
clock = pygame.time.Clock()

# Define the regions for each component
regions = {
    "rpm":      (0, 0, SCREEN_WIDTH//3, SCREEN_HEIGHT//2),
    "speed":    (SCREEN_WIDTH//3, 0, SCREEN_WIDTH//3, SCREEN_HEIGHT//2),
    "fuel":     (2*SCREEN_WIDTH//3, 0, SCREEN_WIDTH//3, SCREEN_HEIGHT//2),
    "time":     (0, SCREEN_HEIGHT//2, SCREEN_WIDTH//3, SCREEN_HEIGHT//2),
    "media":    (SCREEN_WIDTH//3, SCREEN_HEIGHT//2, SCREEN_WIDTH//3, SCREEN_HEIGHT//2),
    "messages": (2*SCREEN_WIDTH//3, SCREEN_HEIGHT//2, SCREEN_WIDTH//3, SCREEN_HEIGHT//2)
}

# Base Component class
class Component:
    def __init__(self, region, name):
        self.region = region
        self.name = name
        self.x = region[0]
        self.y = region[1]
        self.width = region[2]
        self.height = region[3]
        self.center_x = self.width // 2
        self.center_y = self.height // 2

        # Socket for receiving data
        self.socket_thread = None
        self.data_lock = threading.Lock()
        
    def draw_component_background(self, surface):
        # Draw component background with border
        pygame.draw.rect(surface, (30, 30, 40), 
                        (0, 0, self.width, self.height))
        pygame.draw.rect(surface, (100, 100, 120), 
                        (0, 0, self.width, self.height), 2)
        
        # Draw component title
        font = pygame.font.SysFont('Arial', 18)
        title = font.render(self.name, True, (180, 180, 200))
        title_rect = title.get_rect(midtop=(self.center_x, 10))
        surface.blit(title, title_rect)
    
    def update(self):
        pass
    
    def draw(self, surface):
        self.draw_component_background(surface)
    
    def start_socket_listener(self, port):
        self.socket_thread = threading.Thread(target=self._socket_listener, args=(port,))
        self.socket_thread.daemon = True
        self.socket_thread.start()
    
    def _socket_listener(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            sock.bind(('localhost', port))
            sock.listen(1)
            print(f"{self.name} listening on port {port}")
            
            while True:
                conn, addr = sock.accept()
                print(f"{self.name} connected to {addr}")
                
                try:
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        
                        with self.data_lock:
                            self._process_data(data)
                            
                except Exception as e:
                    print(f"{self.name} connection error: {e}")
                finally:
                    conn.close()
        except Exception as e:
            print(f"{self.name} socket error: {e}")
        finally:
            sock.close()
    
    def _process_data(self, data):
        # Override in subclasses
        pass


# RPM Gauge Component
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


# Speed Gauge Component
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


# Fuel Gauge Component
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


# Clock Component
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


# Media Information Component
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


# Messages Component
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


# Create components
components = {
    "rpm": RPMGauge(regions["rpm"]),
    "speed": SpeedGauge(regions["speed"]),
    "fuel": FuelGauge(regions["fuel"]),
    "time": ClockWidget(regions["time"]),
    "media": MediaInfoWidget(regions["media"]),
    "messages": MessagesWidget(regions["messages"])
}

# Start simulation mode for all components
for component in components.values():
    component.start_simulation()

# Main loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    # Update components
    for component in components.values():
        component.update()
    
    # Clear screen
    screen.fill(BG_COLOR)
    
    # Draw grid lines
    for x in range(0, SCREEN_WIDTH, SCREEN_WIDTH // 3):
        pygame.draw.line(screen, (40, 40, 60), (x, 0), (x, SCREEN_HEIGHT), 2)
    for y in range(0, SCREEN_HEIGHT, SCREEN_HEIGHT // 2):
        pygame.draw.line(screen, (40, 40, 60), (0, y), (SCREEN_WIDTH, y), 2)
    
    # Draw components using subsurfaces
    for name, component in components.items():
        region = regions[name]
        subsurface = screen.subsurface(pygame.Rect(region))
        component.draw(subsurface)
    
    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
