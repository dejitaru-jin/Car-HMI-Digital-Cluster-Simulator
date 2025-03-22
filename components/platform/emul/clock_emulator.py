import time
import json
from datetime import datetime
from .data_emulator_base import DataEmulatorBase
from core.constants import *

class ClockEmulator(DataEmulatorBase):
    """Emulator for clock/time data.
    
    Provides real-time clock data for the dashboard, with options
    for time format settings.
    """
    def __init__(self, port=CLOCK_PORT, update_interval=0.5):
        """Initialize the clock data emulator.
        
        Args:
            port (int): Port number for the socket connection
            update_interval (float): Time between data updates in seconds
        """
        super().__init__(port, update_interval)
        self.time_format = "24h"  # can be "12h" or "24h"
        self.show_seconds = True
        self.show_date = True
        self.date_format = "%d %b %Y"  # Day Month Year
    
    def set_time_format(self, format_str):
        """Set the time format.
        
        Args:
            format_str (str): Either "12h" or "24h"
        """
        if format_str in ["12h", "24h"]:
            self.time_format = format_str
    
    def set_show_seconds(self, show):
        """Set whether to show seconds.
        
        Args:
            show (bool): True to show seconds, False to hide
        """
        self.show_seconds = bool(show)
    
    def set_show_date(self, show):
        """Set whether to show date.
        
        Args:
            show (bool): True to show date, False to hide
        """
        self.show_date = bool(show)
    
    def set_date_format(self, format_str):
        """Set the date format string.
        
        Args:
            format_str (str): A strftime format string
        """
        self.date_format = format_str
    
    def _generate_data(self):
        """Generate current time data.
        
        Returns:
            str: JSON string with time information
        """
        now = datetime.now()
        
        # Format time based on settings
        if self.time_format == "12h":
            hour = now.hour % 12
            if hour == 0:
                hour = 12
            ampm = "AM" if now.hour < 12 else "PM"
            
            if self.show_seconds:
                time_str = f"{hour}:{now.minute:02d}:{now.second:02d} {ampm}"
            else:
                time_str = f"{hour}:{now.minute:02d} {ampm}"
        else:  # 24h format
            if self.show_seconds:
                time_str = f"{now.hour:02d}:{now.minute:02d}:{now.second:02d}"
            else:
                time_str = f"{now.hour:02d}:{now.minute:02d}"
        
        # Format date if needed
        date_str = now.strftime(self.date_format) if self.show_date else ""
        
        # Create data structure with all info needed by the widget
        data = {
            "time": time_str,
            "date": date_str,
            "hour": now.hour,
            "minute": now.minute,
            "second": now.second,
            "timestamp": time.time()
        }
        
        # Return as JSON string
        return json.dumps(data)