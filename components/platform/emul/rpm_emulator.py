import random
from .data_emulator_base import DataEmulatorBase
from core.constants import *

class RPMEmulator(DataEmulatorBase):
    """Emulator for engine RPM data.
    
    Generates realistic RPM values that mimic engine behavior, including
    acceleration, deceleration, and idle patterns.
    """
    def __init__(self, port=RPM_PORT, update_interval=0.05):
        """Initialize the RPM data emulator.
        
        Args:
            port (int): Port number for the socket connection
            update_interval (float): Time between data updates in seconds
        """
        super().__init__(port, update_interval)
        self.rpm = 800  # Start at idle RPM
        self.max_rpm = 8000
        self.min_rpm = 800
        
        # Behavior parameters
        self.rpm_change_probability = 0.8  # Probability of RPM changing
        self.acceleration_probability = 0.5  # Probability of acceleration vs deceleration
        self.acceleration_factor = (50, 200)  # Min/max RPM increase during acceleration
        self.deceleration_factor = (50, 150)  # Min/max RPM decrease during deceleration
        
        # Engine state can be 'idle', 'accelerating', 'cruising', 'decelerating'
        self.engine_state = 'idle'
        self.state_duration = 0
        self.max_state_duration = 100  # Maximum ticks in a state before considering state change
    
    def _update_engine_state(self):
        """Update the engine state based on current RPM and probabilistic model."""
        self.state_duration += 1
        
        # Consider state change after some duration
        if self.state_duration > self.max_state_duration or random.random() < 0.05:
            # Transition probabilities depend on current state and RPM
            if self.engine_state == 'idle':
                # More likely to accelerate from idle
                if random.random() < 0.7:
                    self.engine_state = 'accelerating'
            elif self.engine_state == 'accelerating':
                if self.rpm > 3000:
                    # More likely to cruise or decelerate at higher RPMs
                    self.engine_state = random.choice(['cruising', 'decelerating'])
            elif self.engine_state == 'cruising':
                # Equal chance of acceleration or deceleration
                self.engine_state = random.choice(['accelerating', 'decelerating'])
            elif self.engine_state == 'decelerating':
                if self.rpm < 1200:
                    # Return to idle when RPM is low
                    self.engine_state = 'idle'
                else:
                    # May start accelerating again
                    self.engine_state = random.choice(['idle', 'accelerating', 'cruising'])
            
            # Reset duration counter
            self.state_duration = 0
    
    def _generate_data(self):
        """Generate realistic RPM data based on engine state.
        
        Returns:
            int: The current RPM value
        """
        # Update engine state
        self._update_engine_state()
        
        # Modify RPM based on current state
        if random.random() < self.rpm_change_probability:
            if self.engine_state == 'idle':
                # Small fluctuations around idle
                self.rpm += random.randint(-30, 30)
            elif self.engine_state == 'accelerating':
                # Larger increases
                self.rpm += random.randint(*self.acceleration_factor)
            elif self.engine_state == 'cruising':
                # Small fluctuations
                self.rpm += random.randint(-50, 50)
            elif self.engine_state == 'decelerating':
                # Decreases
                self.rpm -= random.randint(*self.deceleration_factor)
        
        # Ensure RPM stays within bounds
        self.rpm = max(self.min_rpm, min(self.rpm, self.max_rpm))
        
        return self.rpm
    