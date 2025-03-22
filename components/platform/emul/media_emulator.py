import random
import json
import time
from .data_emulator_base import DataEmulatorBase
from core.constants import *

class MediaEmulator(DataEmulatorBase):
    """Emulator for media player data.
    
    Generates simulated music player information including track info,
    playback status, and progress.
    """
    def __init__(self, port=MEDIA_PORT, update_interval=0.5):
        """Initialize the media data emulator.
        
        Args:
            port (int): Port number for the socket connection
            update_interval (float): Time between data updates in seconds
        """
        super().__init__(port, update_interval)
        
        # Sample tracks for simulation
        self.tracks = [
            {"title": "Highway Star", "artist": "Deep Purple", "album": "Machine Head", "duration": 368},
            {"title": "Back in Black", "artist": "AC/DC", "album": "Back in Black", "duration": 255},
            {"title": "Hotel California", "artist": "Eagles", "album": "Hotel California", "duration": 391},
            {"title": "Bohemian Rhapsody", "artist": "Queen", "album": "A Night at the Opera", "duration": 354},
            {"title": "Sweet Child O' Mine", "artist": "Guns N' Roses", "album": "Appetite for Destruction", "duration": 356},
            {"title": "Stairway to Heaven", "artist": "Led Zeppelin", "album": "Led Zeppelin IV", "duration": 482},
            {"title": "Free Bird", "artist": "Lynyrd Skynyrd", "album": "Pronounced Leh-nerd Skin-nerd", "duration": 558},
            {"title": "Beat It", "artist": "Michael Jackson", "album": "Thriller", "duration": 258},
            {"title": "Sweet Home Alabama", "artist": "Lynyrd Skynyrd", "album": "Second Helping", "duration": 283},
            {"title": "Thunderstruck", "artist": "AC/DC", "album": "The Razors Edge", "duration": 292}
        ]
        
        # Initial state
        self.current_track_index = random.randint(0, len(self.tracks) - 1)
        self.playing = False
        self.current_position = 0
        self.repeat_mode = "off"  # "off", "single", "all"
        self.shuffle_mode = False
        self.volume = 75
        self.start_time = time.time()
    
    def play(self):
        """Start playback."""
        self.playing = True
        self.start_time = time.time() - self.current_position
    
    def pause(self):
        """Pause playback."""
        self.playing = False
        self.current_position = time.time() - self.start_time
    
    def next_track(self):
        """Move to the next track."""
        if self.shuffle_mode:
            self.current_track_index = random.randint(0, len(self.tracks) - 1)
        else:
            self.current_track_index = (self.current_track_index + 1) % len(self.tracks)
        self.current_position = 0
        self.start_time = time.time()
    
    def prev_track(self):
        """Move to the previous track."""
        if self.current_position > 3:
            # If more than 3 seconds into track, restart it
            self.current_position = 0
            self.start_time = time.time()
        else:
            # Otherwise go to previous track
            if self.shuffle_mode:
                self.current_track_index = random.randint(0, len(self.tracks) - 1)
            else:
                self.current_track_index = (self.current_track_index - 1) % len(self.tracks)
            self.current_position = 0
            self.start_time = time.time()
    
    def toggle_shuffle(self):
        """Toggle shuffle mode."""
        self.shuffle_mode = not self.shuffle_mode
    
    def set_volume(self, volume):
        """Set volume level.
        
        Args:
            volume (int): Volume level from 0 to 100
        """
        self.volume = max(0, min(100, volume))
    
    def cycle_repeat_mode(self):
        """Cycle through repeat modes."""
        modes = ["off", "single", "all"]
        current_index = modes.index(self.repeat_mode)
        self.repeat_mode = modes[(current_index + 1) % len(modes)]
    
    def _update_position(self):
        """Update the current position based on playing state."""
        if self.playing:
            # Update position based on elapsed time
            self.current_position = time.time() - self.start_time
            current_track = self.tracks[self.current_track_index]
            
            # Handle track completion
            if self.current_position >= current_track["duration"]:
                if self.repeat_mode == "single":
                    # Restart the same track
                    self.current_position = 0
                    self.start_time = time.time()
                elif self.repeat_mode == "all" or self.shuffle_mode:
                    # Move to next track
                    self.next_track()
                elif self.current_track_index < len(self.tracks) - 1:
                    # Move to next track if not at the end
                    self.next_track()
                else:
                    # Stop playback at the end
                    self.playing = False
                    self.current_position = current_track["duration"]
    
    def _generate_data(self):
        """Generate media player data.
        
        Returns:
            str: JSON string with media information
        """
        # Update position
        self._update_position()
        
        # Get current track
        current_track = self.tracks[self.current_track_index]
        
        # Calculate progress percentage
        if current_track["duration"] > 0:
            progress = min(100, (self.current_position / current_track["duration"]) * 100)
        else:
            progress = 0
        
        # Create media data
        data = {
            "title": current_track["title"],
            "artist": current_track["artist"],
            "album": current_track["album"],
            "duration": current_track["duration"],
            "position": int(self.current_position),
            "progress": round(progress, 1),
            "playing": self.playing,
            "repeat_mode": self.repeat_mode,
            "shuffle_mode": self.shuffle_mode,
            "volume": self.volume
        }
        
        # Randomly change state
        if random.random() < 0.01:  # 1% chance per update
            action = random.choice(["play", "pause", "next", "prev", "shuffle", "repeat", "none"])
            if action == "play" and not self.playing:
                self.play()
            elif action == "pause" and self.playing:
                self.pause()
            elif action == "next":
                self.next_track()
            elif action == "prev":
                self.prev_track()
            elif action == "shuffle":
                self.toggle_shuffle()
            elif action == "repeat":
                self.cycle_repeat_mode()
            # "none" does nothing
        
        # Return as JSON string
        return json.dumps(data)