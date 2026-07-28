import random
import pygame
import settings
from settings import WHITE, DARK_GRAY, GREEN, GRAY, YELLOW, RED, BLACK
from utils.fonts import get_font


# --- Hit Feedback State ---
shake_duration = 0
shake_intensity = 0
slowmo_duration = 0
slowmo_factor = 1.0

# --- Constant Background Shake (always-on, slight) ---
CONSTANT_SHAKE_INTENSITY = 1
_const_shake_x = 0
_const_shake_y = 0


def draw_text(surface, text, size, x, y, color=WHITE, center_x=False):
    font = get_font(size)
    text_surface = font.render(text, True, color)
    if center_x:
        text_rect = text_surface.get_rect(center=(x, y))
        surface.blit(text_surface, text_rect)
    else:
        surface.blit(text_surface, (x, y))


def create_starfield(num_stars=100):
    stars = []
    for _ in range(num_stars):
        x = random.randint(0, settings.WIDTH)
        y = random.randint(0, settings.HEIGHT)
        speed = random.uniform(0.5, 3.0)
        stars.append([x, y, speed])
    return stars


def update_and_draw_stars(surface, stars, offset_x=0, offset_y=0):
    for star in stars:
        star[1] += star[2]
        if star[1] > settings.HEIGHT:
            star[1] = 0
            star[0] = random.randint(0, settings.WIDTH)
        brightness = int(100 + star[2] * 50)
        color = (brightness, brightness, brightness)
        pygame.draw.circle(surface, color, (int(star[0] + offset_x), int(star[1] + offset_y)), 1)


def draw_volume_bar(surface, x, y, value, label):
    draw_text(surface, label, 28, x, y, WHITE)
    bar_x = x
    bar_y = y + 35
    bar_width = 200
    bar_height = 20
    pygame.draw.rect(surface, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
    fill_width = int(bar_width * value)
    pygame.draw.rect(surface, GREEN, (bar_x, bar_y, fill_width, bar_height))
    draw_text(surface, f"{int(value * 100)}%", 24, bar_x + bar_width + 20, bar_y, WHITE)


def trigger_hit_feedback():
    global shake_duration, shake_intensity, slowmo_duration, slowmo_factor
    shake_duration = 20
    shake_intensity = 12
    slowmo_duration = 25
    slowmo_factor = 0.3


def update_hit_feedback():
    global shake_duration, slowmo_duration, slowmo_factor
    if slowmo_duration > 0:
        slowmo_duration -= 1
        if slowmo_duration == 0:
            slowmo_factor = 1.0
    if shake_duration > 0:
        shake_duration -= 1

    if shake_duration > 0:
        offset_x = random.randint(-shake_intensity, shake_intensity)
        offset_y = random.randint(-shake_intensity, shake_intensity)
    else:
        offset_x = 0
        offset_y = 0
    return offset_x, offset_y


def get_slowmo_factor():
    return slowmo_factor


def update_constant_shake():
    """Update the always-on slight background shake. Call once per frame.
    Returns the new (x, y) offset so the caller can use it directly."""
    global _const_shake_x, _const_shake_y
    _const_shake_x = random.randint(-CONSTANT_SHAKE_INTENSITY, CONSTANT_SHAKE_INTENSITY)
    _const_shake_y = random.randint(-CONSTANT_SHAKE_INTENSITY, CONSTANT_SHAKE_INTENSITY)
    return _const_shake_x, _const_shake_y


def get_constant_shake_offset():
    """Return the current constant shake offset (does not tick state)."""
    return _const_shake_x, _const_shake_y


# ============================================================
# MOUSE / MENU INTERACTION HELPERS
# ============================================================

def point_in_rect(px, py, rect):
    """True if (px, py) is inside the given rect (or rect-like with x,y,w,h)."""
    return (rect.x <= px <= rect.x + rect.width
            and rect.y <= py <= rect.y + rect.height)


def value_from_slider_x(mouse_x, bar_x, bar_width):
    """Convert an x position within a slider's bar into a 0.0-1.0 value."""
    if bar_width <= 0:
        return 0.0
    rel = (mouse_x - bar_x) / bar_width
    if rel < 0.0:
        rel = 0.0
    elif rel > 1.0:
        rel = 1.0
    return rel


def draw_button(surface, rect, label, font_size, base_color, hover_color, text_color=WHITE):
    """Draw a button rect with a label centered inside. Returns True if hovered
    (so callers can chain a different border if they want)."""
    hovered = point_in_rect(*pygame.mouse.get_pos(), rect)
    color = hover_color if hovered else base_color
    pygame.draw.rect(surface, color, rect)
    pygame.draw.rect(surface, WHITE, rect, 2)
    font = get_font(font_size)
    text = font.render(label, True, text_color)
    text_rect = text.get_rect(center=rect.center)
    surface.blit(text, text_rect)
    return hovered