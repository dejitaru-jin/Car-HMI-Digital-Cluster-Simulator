import random
from .data_emulator_base import DataEmulatorBase
from core.constants import *

class FuelEmulator(DataEmulatorBase):
    """Emulator for fuel level data.
    
    Generates realistic fuel level values that decrease over time
    with occasional refill events.
    """
    def __init__(self, port=FUEL_GAUGE_PORT, update_interval=1.0):
        """Initialize the fuel data emulator.
        
        Args:
            port (int): Port number for the socket connection
            update_interval (float): Time between data updates in seconds
        """
        super().__init__(port, update_interval)
        self.fuel_level = 100.0  # Start with full tank (percentage)
        self.max_fuel = 100.0
        self.tank_capacity = 60.0  # Liters
        
        # Behavior parameters
        self.base_consumption_rate = 0.01  # Percentage per update
        self.consumption_variance = 0.005  # Random variance in consumption
        self.refill_probability = 0.0005   # Chance of refill event per update
        self.refill_speed = 2.0            # Percentage per update during refill
        
        # Fuel state can be 'consuming' or 'refilling'
        self.fuel_state = 'consuming'
        
        # Correlation with speed (will be a future enhancement)
        self.speed_correlation = False
        self.current_speed = 0
    
    def update_speed(self, speed):
        """Update the current speed for consumption correlation.
        
        Args:
            speed (float): Current vehicle speed
        """
        self.current_speed = speed
        
    def _calculate_consumption(self):
        """Calculate fuel consumption rate based on current state.
        
        Returns:
            float: Amount of fuel to consume in this update
        """
        # Base consumption with random variance
        consumption = self.base_consumption_rate + random.uniform(
            -self.consumption_variance, self.consumption_variance)
        
        # In the future, correlate with speed
        if self.speed_correlation and self.current_speed > 0:
            # Higher consumption at higher speeds
            speed_factor = 1.0 + (self.current_speed / 100.0)
            consumption *= speed_factor
            
        return max(0, consumption)
    
    def _generate_data(self):
        """Generate realistic fuel level data.
        
        Returns:
            float: The current fuel level as a percentage
        """

        print(f"Fuel generating data")
        if self.fuel_state == 'consuming':
            print(f"Fuel generating data: consuming")

        # Random chance to switch to refill state if low
        if (self.fuel_state == 'consuming' and 
            self.fuel_level < 15.0 and 
            random.random() < self.refill_probability * 10):
            self.fuel_state = 'refilling'
        
        # Random chance to switch to refill state normally
        elif (self.fuel_state == 'consuming' and 
              random.random() < self.refill_probability):
            self.fuel_state = 'refilling'
        
        # Update fuel level based on state
        if self.fuel_state == 'consuming':
            # Reduce fuel level
            self.fuel_level -= self._calculate_consumption()
            print(f"Fuel generating data: {self.fuel_level}")
            
            # Ensure not negative
            self.fuel_level = max(0, self.fuel_level)
            
        elif self.fuel_state == 'refilling':
            # Increase fuel level
            self.fuel_level += self.refill_speed
            
            # Check if full
            if self.fuel_level >= self.max_fuel:
                self.fuel_level = self.max_fuel
                self.fuel_state = 'consuming'
        
        # Return current level rounded to one decimal place
        print(f"Fuel generating data. fuel_level: {round(self.fuel_level, 1)}")
        return round(self.fuel_level, 1)