# settings.py
# Central configuration for Orbit Overdrive.
#
# Phase 1A: we keep the original names (MONITOR_WIDTH, calculate_resolution,
# apply_display_mode, etc.) as compatibility shims so main.py doesn't need
# to change its imports in this step. The NEW way of doing things is the
# VIRTUAL_* constants + update_for_display() function — those are what
# the mobile port will use.

# --- Virtual (design) resolution ---
# Game logic is designed at this fixed resolution. Phases 2+ will scale
# the playfield to fit whatever the actual device surface is.
VIRTUAL_WIDTH = 1280
VIRTUAL_HEIGHT = 720

# --- Runtime state (set by main.py after creating the display) ---
WIDTH = VIRTUAL_WIDTH
HEIGHT = VIRTUAL_HEIGHT
SCALE_FACTOR = 1.0
DISPLAY_WIDTH = VIRTUAL_WIDTH
DISPLAY_HEIGHT = VIRTUAL_HEIGHT
LETTERBOX_OFFSET_X = 0
LETTERBOX_OFFSET_Y = 0

# --- Mode flags ---
MOBILE_MODE = False
# --- Debug flags ---
# FORCE_TOUCH_UI: when True, the on-screen touch UI is shown and the
# touch input layer is used. Useful for previewing the mobile UI on
# a desktop. Toggle in-game with F10. Defaults to False on desktop,
# True on Android/iOS (set automatically at runtime).
FORCE_TOUCH_UI = False


# --- Window mode (desktop only) ---
WINDOW_SCALE = 0.7
is_fullscreen = True

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
DARK_BLUE = (0, 50, 150)

# --- Gameplay ---
FPS = 60

# ============================================================
# NEW: virtual-resolution aware display update
# ============================================================
def update_for_display(screen):
    """Recompute SCALE_FACTOR and letterbox offsets for the current
    display surface. Pass in the actual pygame display surface.
    Used by Phase 2+; Phase 1 main.py doesn't call this yet."""
    global WIDTH, HEIGHT, SCALE_FACTOR
    global DISPLAY_WIDTH, DISPLAY_HEIGHT
    global LETTERBOX_OFFSET_X, LETTERBOX_OFFSET_Y

    DISPLAY_WIDTH, DISPLAY_HEIGHT = screen.get_size()

    scale_x = DISPLAY_WIDTH / VIRTUAL_WIDTH
    scale_y = DISPLAY_HEIGHT / VIRTUAL_HEIGHT
    scale = min(scale_x, scale_y)

    WIDTH = max(1, int(VIRTUAL_WIDTH * scale))
    HEIGHT = max(1, int(VIRTUAL_HEIGHT * scale))
    SCALE_FACTOR = scale

    LETTERBOX_OFFSET_X = (DISPLAY_WIDTH - WIDTH) // 2
    LETTERBOX_OFFSET_Y = (DISPLAY_HEIGHT - HEIGHT) // 2


# ============================================================
# COMPATIBILITY SHIMS — preserve the old API surface so main.py
# doesn't have to change its imports in Phase 1A. These will be
# removed in a later phase when main.py is updated.
# ============================================================

# Read the monitor once at module load (same as the original file did).
# This works on desktop. On Android we'll never call this code path.
import pygame
_display_info = pygame.display.Info()
MONITOR_WIDTH = _display_info.current_w or VIRTUAL_WIDTH
MONITOR_HEIGHT = _display_info.current_h or VIRTUAL_HEIGHT
MONITOR_ASPECT = (MONITOR_WIDTH / MONITOR_HEIGHT) if MONITOR_HEIGHT else (16 / 9)


def calculate_resolution(fullscreen):
    """Legacy: pick a windowed or fullscreen resolution from the monitor."""
    if fullscreen:
        return MONITOR_WIDTH, MONITOR_HEIGHT
    window_height = int(MONITOR_HEIGHT * WINDOW_SCALE)
    window_width = int(window_height * MONITOR_ASPECT)
    return window_width, window_height


def get_scale_factor(height):
    """Legacy: original game was designed at height 600."""
    return height / 600


def apply_display_mode(fullscreen, width, height):
    """Legacy: create a fullscreen or windowed display surface."""
    flags = pygame.FULLSCREEN if fullscreen else 0
    return pygame.display.set_mode((width, height), flags)
