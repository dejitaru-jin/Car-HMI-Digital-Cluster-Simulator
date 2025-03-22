import random
from .data_emulator_base import DataEmulatorBase
from core.constants import *

class SpeedEmulator(DataEmulatorBase):
    """Emulator for vehicle speed data.
    
    Generates realistic speed values that mimic vehicle behavior, including
    acceleration, deceleration, cruising, and stop patterns.
    """
    def __init__(self, port=SPEED_GAUGE_PORT, update_interval=0.1):
        """Initialize the speed data emulator.
        
        Args:
            port (int): Port number for the socket connection
            update_interval (float): Time between data updates in seconds
        """
        super().__init__(port, update_interval)
        self.speed = 0  # Start at 0 km/h
        self.max_speed = 220
        
        # Behavior parameters
        self.acceleration_rate = 3      # km/h per update during acceleration
        self.deceleration_rate = 2      # km/h per update during deceleration
        self.brake_rate = 5             # km/h per update during braking
        self.target_speed = 0           # Target speed to reach
        
        # Vehicle state can be 'stopped', 'accelerating', 'cruising', 'decelerating', 'braking'
        self.vehicle_state = 'stopped'
        self.state_duration = 0
        self.max_state_duration = 100  # Maximum ticks in a state before considering state change
    
    def _update_vehicle_state(self):
        """Update the vehicle state based on current speed and probabilistic model."""
        self.state_duration += 1
        
        # Consider state change after some duration or randomly
        if self.state_duration > self.max_state_duration or random.random() < 0.03:
            # Transition probabilities depend on current state and speed
            if self.vehicle_state == 'stopped':
                if random.random() < 0.7:  # 70% chance to start moving
                    self.vehicle_state = 'accelerating'
                    self.target_speed = random.randint(30, self.max_speed)
                    
            elif self.vehicle_state == 'accelerating':
                if abs(self.speed - self.target_speed) < 5:  # Close to target
                    self.vehicle_state = 'cruising'
                elif random.random() < 0.1:  # 10% chance to change target
                    self.target_speed = random.randint(int(self.speed), self.max_speed)
                    
            elif self.vehicle_state == 'cruising':
                r = random.random()
                if r < 0.2:  # 20% chance to accelerate
                    self.vehicle_state = 'accelerating'
                    self.target_speed = min(self.speed + random.randint(10, 50), self.max_speed)
                elif r < 0.4:  # 20% chance to decelerate
                    self.vehicle_state = 'decelerating'
                    self.target_speed = max(0, self.speed - random.randint(10, 30))
                elif r < 0.45:  # 5% chance to brake
                    self.vehicle_state = 'braking'
                    self.target_speed = max(0, self.speed - random.randint(30, self.speed))
                    
            elif self.vehicle_state == 'decelerating':
                if abs(self.speed - self.target_speed) < 5:  # Close to target
                    if self.target_speed < 5:
                        self.vehicle_state = 'stopped'
                    else:
                        self.vehicle_state = 'cruising'
                elif random.random() < 0.1:  # 10% chance to brake suddenly
                    self.vehicle_state = 'braking'
                    self.target_speed = max(0, self.speed - random.randint(30, self.speed))
                    
            elif self.vehicle_state == 'braking':
                if self.speed < 5:  # Almost stopped
                    self.vehicle_state = 'stopped'
                    self.speed = 0
                elif abs(self.speed - self.target_speed) < 5:  # Close to target
                    self.vehicle_state = 'cruising'
            
            # Reset duration counter
            self.state_duration = 0
    
    def _generate_data(self):
        """Generate realistic speed data based on vehicle state.
        
        Returns:
            float: The current speed value
        """
        # Update vehicle state
        self._update_vehicle_state()
        
        # Modify speed based on current state
        if self.vehicle_state == 'stopped':
            self.speed = 0
        elif self.vehicle_state == 'accelerating':
            # Add some randomness to acceleration
            self.speed += self.acceleration_rate * (0.8 + 0.4 * random.random())
            if self.speed > self.target_speed:
                self.speed = self.target_speed
        elif self.vehicle_state == 'cruising':
            # Small fluctuations during cruising
            self.speed += random.uniform(-1.0, 1.0)
        elif self.vehicle_state == 'decelerating':
            # Gradual deceleration
            self.speed -= self.deceleration_rate * (0.8 + 0.4 * random.random())
            if self.speed < self.target_speed:
                self.speed = self.target_speed
        elif self.vehicle_state == 'braking':
            # Faster deceleration for braking
            self.speed -= self.brake_rate * (0.8 + 0.4 * random.random())
            if self.speed < self.target_speed:
                self.speed = self.target_speed
        
        # Ensure speed stays within bounds
        self.speed = max(0, min(self.speed, self.max_speed))
        
        # Return speed rounded to one decimal place
        return round(self.speed, 1)