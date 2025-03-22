import pygame
import sys
import time
from core.constants import *
from components.gauges.rpm_gauge import RPMGauge
from components.gauges.speed_gauge import SpeedGauge
from components.gauges.fuel_gauge import FuelGauge
from components.info.clock_widget import ClockWidget
from components.info.media_widget import MediaInfoWidget
from components.info.messages_widget import MessagesWidget

# Import emulators
from components.platform.emul.rpm_emulator import RPMEmulator
from components.platform.emul.speed_emulator import SpeedEmulator
from components.platform.emul.fuel_emulator import FuelEmulator
from components.platform.emul.clock_emulator import ClockEmulator
from components.platform.emul.media_emulator import MediaEmulator
from components.platform.emul.messages_emulator import MessagesEmulator

# Initialize pygame
pygame.init()

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Car Digital Cluster Simulator")
clock = pygame.time.Clock()

def main():
    # Start data emulators (each on a different port)
    emulators = {
        "rpm": RPMEmulator(port=RPM_PORT),
        "speed": SpeedEmulator(port=SPEED_GAUGE_PORT),
        "fuel": FuelEmulator(port=FUEL_GAUGE_PORT),
        "time": ClockEmulator(port=CLOCK_PORT),
        "media": MediaEmulator(port=MEDIA_PORT),
        "messages": MessagesEmulator(port=MESSAGES_PORT)
    }
    
    # Start all emulators
    for emulator in emulators.values():
        emulator.start()
    
    # Create components
    components = {
        "rpm": RPMGauge(regions["rpm"], port=RPM_PORT),
        "speed": SpeedGauge(regions["speed"], port=SPEED_GAUGE_PORT),
        "fuel": FuelGauge(regions["fuel"], port=FUEL_GAUGE_PORT),
        "time": ClockWidget(regions["time"], port=CLOCK_PORT),
        "media": MediaInfoWidget(regions["media"], port=MEDIA_PORT),
        "messages": MessagesWidget(regions["messages"], port=MESSAGES_PORT)
    }

    # Connect components to data sources
    for component in components.values():
        component.connect()

    # Main loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                print(f"Received event:{event}, type:{event.type}, key:{event.key}")
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_w:
                    for component in components.values():
                        component.send_key(pygame.K_w)
                elif event.key == pygame.K_q:
                    running = False
        
        # Update components (now only handles UI updates, data comes from emulators)
        for component in components.values():
            component.update()
        
        # Clear screen
        screen.fill(BG_COLOR)
        
        # Draw grid lines
        for x in range(0, SCREEN_WIDTH, SCREEN_WIDTH // 3):
            pygame.draw.line(screen, CHARCOAL_2, (x, 0), (x, SCREEN_HEIGHT), 2)
        for y in range(0, SCREEN_HEIGHT, SCREEN_HEIGHT // 2):
            pygame.draw.line(screen, CHARCOAL_2, (0, y), (SCREEN_WIDTH, y), 2)
        
        # Draw components using subsurfaces
        for name, component in components.items():
            region = regions[name]
            subsurface = screen.subsurface(pygame.Rect(region))
            component.draw(subsurface)
        
        # Update display
        pygame.display.flip()
        clock.tick(60)

    # Clean up: disconnect components and stop emulators
    for component in components.values():
        component.disconnect()
    
    for emulator in emulators.values():
        emulator.stop()
    
    # Wait for threads to clean up
    time.sleep(0.5)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()