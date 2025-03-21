import socket
import threading
import time

class DataSource:
    """Base class for data sources that connect to emulators or real hardware.
    
    This class handles the socket connection to a data provider and
    parses the incoming data for component use.
    """
    def __init__(self, host='localhost', port=None, reconnect_interval=1.0):
        """Initialize the data source.
        
        Args:
            host (str): The hostname to connect to
            port (int): The port number to connect to
            reconnect_interval (float): Time to wait between reconnection attempts
        """
        self.host = host
        self.port = port
        self.reconnect_interval = reconnect_interval
        self.socket = None
        self.connected = False
        self.running = False
        self.thread = None
        self.data_callback = None
    
    def set_port(self, port):
        """Set the port to connect to.
        
        Args:
            port (int): The port number
        """
        self.port = port
    
    def set_data_callback(self, callback):
        """Set the callback function to handle received data.
        
        Args:
            callback (callable): Function that takes a data parameter
        """
        self.data_callback = callback
    
    def connect(self):
        """Connect to the data source."""
        if self.port is None:
            raise ValueError("Port must be set before connecting")
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(1.0)  # Timeout for connection attempts
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"Connected to data source at {self.host}:{self.port}")
            return True
        except socket.error as e:
            print(f"Failed to connect to data source: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from the data source."""
        if self.socket:
            self.socket.close()
        self.connected = False
    
    def start(self):
        """Start the data reception thread."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._receive_data_loop)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        """Stop the data reception thread and disconnect."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        self.disconnect()
    
    def _receive_data_loop(self):
        """Main thread function that receives and processes data."""
        while self.running:
            # Try to connect if not connected
            if not self.connected:
                if self.connect():
                    # Successfully connected
                    pass
                else:
                    # Failed to connect, wait and try again
                    time.sleep(self.reconnect_interval)
                    continue
            
            # Receive data
            try:
                data = self.socket.recv(1024)
                if not data:
                    # Connection closed
                    print("Connection closed by server")
                    self.connected = False
                    continue
                
                # Process the data
                self._process_data(data)
            except socket.timeout:
                # No data available, continue
                pass
            except socket.error as e:
                print(f"Socket error: {e}")
                self.connected = False
                time.sleep(self.reconnect_interval)
    
    def _process_data(self, data):
        """Process received data and call callback if set.
        
        Args:
            data (bytes): The received data
        """
        if self.data_callback:
            self.data_callback(data)