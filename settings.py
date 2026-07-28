import pygame

# --- Display Detection ---
display_info = pygame.display.Info()
MONITOR_WIDTH = display_info.current_w
MONITOR_HEIGHT = display_info.current_h
MONITOR_ASPECT = MONITOR_WIDTH / MONITOR_HEIGHT

# --- Resolution State ---
WINDOW_SCALE = 0.7
is_fullscreen = True

# --- Resolution (computed at runtime in main.py) ---
WIDTH = MONITOR_WIDTH
HEIGHT = MONITOR_HEIGHT
SCALE_FACTOR = HEIGHT / 600


def calculate_resolution(fullscreen):
    """Calculate game resolution based on fullscreen/windowed mode."""
    if fullscreen:
        return MONITOR_WIDTH, MONITOR_HEIGHT
    else:
        window_height = int(MONITOR_HEIGHT * WINDOW_SCALE)
        window_width = int(window_height * MONITOR_ASPECT)
        return window_width, window_height


def get_scale_factor(height):
    """Reference: the original game was designed at height 600."""
    return height / 600


def apply_display_mode(fullscreen, width, height):
    """Returns a new pygame display surface with the requested mode."""
    flags = pygame.FULLSCREEN if fullscreen else 0
    return pygame.display.set_mode((width, height), flags)


# --- Colors ---
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
PURPLE = (200, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (80, 80, 80)
LIGHT_GRAY = (180, 180, 180)
MEDIUM_GRAY = (140, 140, 140)
DARK_BROWN = (101, 67, 33)
LIGHT_BROWN = (139, 90, 43)
LIGHT_BLUE = (100, 200, 255)
LIGHT_GRAY = (180, 180, 180)
LIGHT_BROWN = (139, 90, 43)
DARK_BLUE = (0, 50, 150)

# --- Gameplay ---
FPS = 60