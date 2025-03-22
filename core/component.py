import pygame
import threading
import socket
from core.constants import *

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
        pygame.draw.rect(surface, DARK_BLUE_GRAY, 
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
        
    def start_simulation(self):
        # Override in subclasses
        pass

    def send_key(self, key):
        # Override in subclasses if needed
        pass
