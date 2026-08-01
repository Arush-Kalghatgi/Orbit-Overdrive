# settings.py
# Central configuration for Orbit Overdrive (desktop build).
#
# The game renders directly at the real window/monitor resolution —
# no virtual canvas, no scaling surface. WIDTH/HEIGHT change when you
# toggle fullscreen, and SCALE_FACTOR adjusts speeds so gameplay feels
# consistent across resolutions.

import pygame

BASE_HEIGHT = 600  # reference height SCALE_FACTOR is calculated against

MONITOR_WIDTH = 0
MONITOR_HEIGHT = 0
MONITOR_ASPECT = 16 / 9

WINDOW_SCALE = 0.85  # windowed mode height, as a fraction of monitor height

WIDTH = 1280
HEIGHT = 720
SCALE_FACTOR = 1.0

is_fullscreen = True

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
DARK_BLUE = (0, 50, 150)
BLUE = (60, 120, 230)

FPS = 60


def init_monitor_info():
    """Call once, right after pygame.init(), before creating the window."""
    global MONITOR_WIDTH, MONITOR_HEIGHT, MONITOR_ASPECT
    info = pygame.display.Info()
    MONITOR_WIDTH = info.current_w
    MONITOR_HEIGHT = info.current_h
    MONITOR_ASPECT = MONITOR_WIDTH / MONITOR_HEIGHT


def calculate_resolution(fullscreen):
    """Return (width, height) for the requested mode, always matching
    the monitor's aspect ratio so nothing looks stretched."""
    if fullscreen:
        return MONITOR_WIDTH, MONITOR_HEIGHT
    window_height = int(MONITOR_HEIGHT * WINDOW_SCALE)
    window_width = int(window_height * MONITOR_ASPECT)
    return window_width, window_height


def apply_resolution(fullscreen):
    """Recompute WIDTH/HEIGHT/SCALE_FACTOR for the requested mode."""
    global WIDTH, HEIGHT, SCALE_FACTOR
    WIDTH, HEIGHT = calculate_resolution(fullscreen)
    SCALE_FACTOR = HEIGHT / BASE_HEIGHT
    return WIDTH, HEIGHT