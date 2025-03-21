import random
import json
import time
from .data_emulator_base import DataEmulatorBase

class MessagesEmulator(DataEmulatorBase):
    """Emulator for notification messages data.
    
    Generates simulated notification messages with varying priority levels
    and auto-dismissal behavior.
    """
    def __init__(self, port=5006, update_interval=1.0):
        """Initialize the messages data emulator.
        
        Args:
            port (int): Port number for the socket connection
            update_interval (float): Time between data updates in seconds
        """
        super().__init__(port, update_interval)
        
        # Message templates by category
        self.messages = {
            "info": [
                "Route updated. ETA: {time}",
                "Traffic reported ahead",
                "Weather alert: {condition}",
                "Incoming call from {name}",
                "New text message from {name}",
                "Next service in {distance} km",
                "Software update available",
                "Connected to new Bluetooth device",
                "Navigation recalculating...",
                "Voice command recognized",
            ],
            "warning": [
                "Low fuel warning: {fuel_level}% remaining",
                "Tire pressure low: {wheel} wheel",
                "Oil level low",
                "Battery voltage low",
                "Engine temperature high",
                "Windshield washer fluid low",
                "Brake pad wear detected",
                "Headlight bulb failure",
                "Cruise control deactivated",
                "Lane departure warning",
            ],
            "critical": [
                "BRAKE SYSTEM FAILURE",
                "ENGINE OVERHEATING",
                "AIRBAG SYSTEM ERROR",
                "ABS SYSTEM FAILURE",
                "OIL PRESSURE CRITICAL",
                "POWER STEERING FAILURE",
                "STABILITY CONTROL DISABLED",
                "COLLISION WARNING",
                "TRANSMISSION MALFUNCTION",
                "VEHICLE SECURITY BREACH",
            ]
        }
        
        # Data for message templates
        self.names = ["John", "Sarah", "Michael", "Emily", "David", "Lisa", "Tom", "Jessica"]
        self.weather_conditions = ["Rain", "Snow", "Fog", "High winds", "Hail", "Icy conditions"]
        self.wheels = ["Front left", "Front right", "Rear left", "Rear right"]
        
        # Active messages
        self.active_messages = []
        self.message_id_counter = 0
        
        # Probabilities for new messages
        self.message_probabilities = {
            "info": 0.2,       # 20% chance per update
            "warning": 0.05,   # 5% chance per update
            "critical": 0.01   # 1% chance per update
        }
    
    def _create_message(self, category):
        """Create a new message from the given category.
        
        Args:
            category (str): Message category ("info", "warning", "critical")
            
        Returns:
            dict: Message data
        """
        # Select random template
        template = random.choice(self.messages[category])
        
        # Fill in template variables
        content = template
        if "{name}" in content:
            content = content.replace("{name}", random.choice(self.names))
        if "{time}" in content:
            hours = random.randint(0, 1)
            minutes = random.randint(5, 59)
            content = content.replace("{time}", f"{hours}h {minutes}min")
        if "{condition}" in content:
            content = content.replace("{condition}", random.choice(self.weather_conditions))
        if "{wheel}" in content:
            content = content.replace("{wheel}", random.choice(self.wheels))
        if "{fuel_level}" in content:
            content = content.replace("{fuel_level}", str(random.randint(5, 15)))
        if "{distance}" in content:
            content = content.replace("{distance}", str(random.randint(500, 5000)))
        
        # Create message object
        self.message_id_counter += 1
        message = {
            "id": self.message_id_counter,
            "category": category,
            "content": content,
            "timestamp": time.time(),
            "dismissed": False,
            "acknowledged": False
        }
        
        # Set auto-dismiss time based on category
        if category == "info":
            message["auto_dismiss"] = time.time() + random.randint(5, 15)  # 5-15 seconds
        elif category == "warning":
            message["auto_dismiss"] = time.time() + random.randint(20, 40)  # 20-40 seconds
        else:  # critical
            message["auto_dismiss"] = None  # Never auto-dismiss critical messages
            
        return message
    
    def add_message(self, category, content):
        """Manually add a message.
        
        Args:
            category (str): Message category ("info", "warning", "critical")
            content (str): Message content
        """
        self.message_id_counter += 1
        message = {
            "id": self.message_id_counter,
            "category": category,
            "content": content,
            "timestamp": time.time(),
            "dismissed": False,
            "acknowledged": False
        }
        
        # Set auto-dismiss time based on category
        if category == "info":
            message["auto_dismiss"] = time.time() + 10
        elif category == "warning":
            message["auto_dismiss"] = time.time() + 30
        else:  # critical
            message["auto_dismiss"] = None
            
        self.active_messages.append(message)
    
    def dismiss_message(self, message_id):
        """Dismiss a message by ID.
        
        Args:
            message_id (int): The message ID to dismiss
        """
        for message in self.active_messages:
            if message["id"] == message_id:
                message["dismissed"] = True
                break
    
    def acknowledge_message(self, message_id):
        """Acknowledge a message by ID.
        
        Args:
            message_id (int): The message ID to acknowledge
        """
        for message in self.active_messages:
            if message["id"] == message_id:
                message["acknowledged"] = True
                break
    
    def _update_messages(self):
        """Update message states (auto-dismiss, etc.)."""
        now = time.time()
        
        # Remove dismissed messages
        self.active_messages = [m for m in self.active_messages if not m["dismissed"]]
        
        # Check auto-dismiss times
        for message in self.active_messages:
            if message["auto_dismiss"] and now >= message["auto_dismiss"]:
                message["dismissed"] = True
        
        # Generate new messages
        for category, probability in self.message_probabilities.items():
            if random.random() < probability:
                # Don't add too many messages
                if len(self.active_messages) < 5:
                    self.active_messages.append(self._create_message(category))
    
    def _generate_data(self):
        """Generate message notification data.
        
        Returns:
            str: JSON string with message information
        """
        # Update message states
        self._update_messages()
        
        # Create active messages data
        data = {
            "messages": self.active_messages,
            "count": {
                "total": len(self.active_messages),
                "info": sum(1 for m in self.active_messages if m["category"] == "info"),
                "warning": sum(1 for m in self.active_messages if m["category"] == "warning"),
                "critical": sum(1 for m in self.active_messages if m["category"] == "critical")
            },
            "timestamp": time.time()
        }
        
        # Return as JSON string
        return json.dumps(data)