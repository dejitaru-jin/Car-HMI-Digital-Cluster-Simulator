# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

# Colors
BG_COLOR = (20, 20, 30)  # Dark blue-gray background

# Define the regions for each component
regions = {
    "rpm":      (0, 0, SCREEN_WIDTH//3, SCREEN_HEIGHT//2),
    "speed":    (SCREEN_WIDTH//3, 0, SCREEN_WIDTH//3, SCREEN_HEIGHT//2),
    "fuel":     (2*SCREEN_WIDTH//3, 0, SCREEN_WIDTH//3, SCREEN_HEIGHT//2),
    "time":     (0, SCREEN_HEIGHT//2, SCREEN_WIDTH//3, SCREEN_HEIGHT//2),
    "media":    (SCREEN_WIDTH//3, SCREEN_HEIGHT//2, SCREEN_WIDTH//3, SCREEN_HEIGHT//2),
    "messages": (2*SCREEN_WIDTH//3, SCREEN_HEIGHT//2, SCREEN_WIDTH//3, SCREEN_HEIGHT//2)
}
