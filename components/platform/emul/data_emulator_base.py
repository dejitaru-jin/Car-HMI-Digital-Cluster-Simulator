import threading
import time
import queue
import socket
import struct

class DataEmulatorBase:
    """Base class for data emulation components.
    
    This class provides a common foundation for all data emulators,
    handling socket creation, data delivery, and threading.
    """
    def __init__(self, port, update_interval=0.1):
        """Initialize the data emulator.
        
        Args:
            port (int): The port number to use for the socket connection
            update_interval (float): Time between data updates in seconds
        """
        self.port = port
        self.update_interval = update_interval
        self.running = False
        self.socket = None
        self.thread = None
        self.data_queue = queue.Queue(maxsize=10)  # Buffer some values
    
    def start(self):
        """Start the data emulation thread and socket server."""
        if self.running:
            return
            
        # Create the socket server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('localhost', self.port))
        self.socket.listen(1)
        self.socket.settimeout(0.1)  # Non-blocking socket
        
        # Start the emulation thread
        self.running = True
        self.thread = threading.Thread(target=self._run_emulation)
        self.thread.daemon = True  # Thread will exit when program does
        self.thread.start()
        
        print(f"Data emulator started on port {self.port}")
    
    def stop(self):
        """Stop the data emulation thread and close the socket."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        if self.socket:
            self.socket.close()
        print(f"Data emulator on port {self.port} stopped")
    
    def _run_emulation(self):
        """Main thread function that generates data and handles connections."""
        client = None
        
        while self.running:
            # Accept new connections
            if client is None:
                try:
                    client, addr = self.socket.accept()
                    print(f"Client connected from {addr}")
                    client.settimeout(0.1)  # Non-blocking client socket
                except socket.timeout:
                    # No connection yet, continue
                    pass
            
            # Generate data
            data = self._generate_data()
            if data is not None:
                try:
                    # Add to queue for possible retrieval by direct connection
                    if not self.data_queue.full():
                        self.data_queue.put(data)
                    
                    # Send over socket if client is connected
                    if client:
                        try:
                            client.sendall(str(data).encode())
                        except (socket.error, BrokenPipeError) as e:
                            print(f"Socket error: {e}, client disconnected")
                            client = None
                except Exception as e:
                    print(f"Error sending data: {e}")
            
            # Sleep until next update
            time.sleep(self.update_interval)
    
    def _generate_data(self):
        """Generate emulated data - Override in subclass.
        
        Returns:
            The generated data value
        """
        raise NotImplementedError("Subclasses must implement _generate_data")
    
    def get_latest_data(self):
        """Get the latest data value from the queue (non-blocking).
        
        Returns:
            The latest data value or None if no data is available
        """
        try:
            return self.data_queue.get_nowait()
        except queue.Empty:
            return None
