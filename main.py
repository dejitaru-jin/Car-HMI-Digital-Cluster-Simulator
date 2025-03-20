import pygame
import sys
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, BG_COLOR, regions
from components.gauges.rpm_gauge import RPMGauge
from components.gauges.speed_gauge import SpeedGauge
from components.gauges.fuel_gauge import FuelGauge
from components.info.clock_widget import ClockWidget
from components.info.media_widget import MediaInfoWidget
from components.info.messages_widget import MessagesWidget

# Initialize pygame
pygame.init()

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Car HMI Emulator")
clock = pygame.time.Clock()

def main():
    # Create components
    components = {
        "rpm": RPMGauge(regions["rpm"]),
        "speed": SpeedGauge(regions["speed"]),
        "fuel": FuelGauge(regions["fuel"]),
        "time": ClockWidget(regions["time"]),
        "media": MediaInfoWidget(regions["media"]),
        "messages": MessagesWidget(regions["messages"])
    }

    # Start simulation mode for all components
    for component in components.values():
        component.start_simulation()

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
        
        # Update components
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

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
