import math
import pygame

def draw_arc(surface, color, center, radius, start_angle, end_angle, width=1):
    """
    Draw an arc on the given surface
    
    Args:
        surface: pygame surface to draw on
        color: RGB tuple for arc color
        center: (x, y) tuple for center point
        radius: radius of arc
        start_angle: start angle in radians
        end_angle: end angle in radians
        width: line width, 0 for filled
    """
    rect = pygame.Rect(0, 0, radius*2, radius*2)
    rect.center = center
    
    # Convert radians to degrees for pygame
    start_degrees = start_angle * 180 / math.pi
    end_degrees = end_angle * 180 / math.pi
    
    pygame.draw.arc(surface, color, rect, start_angle, end_angle, width)

def format_time(seconds):
    """
    Format seconds into mm:ss
    
    Args:
        seconds: time in seconds
        
    Returns:
        Formatted string in mm:ss format
    """
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"