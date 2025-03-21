import pygame
import sys
import time
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, BG_COLOR, regions
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
pygame.display.set_caption("Car HMI Emulator")
clock = pygame.time.Clock()

def main():
    # Start data emulators (each on a different port)
    emulators = {
        "rpm": RPMEmulator(port=5001),
        "speed": SpeedEmulator(port=5002),
        "fuel": FuelEmulator(port=5003),
        "time": ClockEmulator(port=5004),
        "media": MediaEmulator(port=5005),
        "messages": MessagesEmulator(port=5006)
    }
    
    # Start all emulators
    for emulator in emulators.values():
        emulator.start()
    
    # Create components
    components = {
        "rpm": RPMGauge(regions["rpm"], port=5001),
        "speed": SpeedGauge(regions["speed"], port=5002),
        "fuel": FuelGauge(regions["fuel"], port=5003),
        "time": ClockWidget(regions["time"], port=5004),
        "media": MediaInfoWidget(regions["media"], port=5005),
        "messages": MessagesWidget(regions["messages"], port=5006)
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
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Update components (now only handles UI updates, data comes from emulators)
        for component in components.values():
            component.update()
        
        # Clear screen
        screen.fill(BG_COLOR)
        
        # Draw grid lines
        for x in range(0, SCREEN_WIDTH, SCREEN_WIDTH // 3):
            pygame.draw.line(screen, (40, 40, 60), (x, 0), (x, SCREEN_HEIGHT), 2)
        for y in range(0, SCREEN_HEIGHT, SCREEN_HEIGHT // 2):
            pygame.draw.line(screen, (40, 40, 60), (0, y), (SCREEN_WIDTH, y), 2)
        
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