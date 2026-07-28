import pygame
import math
import random
import settings
from settings import CYAN, WHITE, RED, YELLOW, GREEN, BLACK, GRAY, DARK_GRAY, PURPLE
from utils.fonts import get_font
from utils.highscore import load_high_score, load_last_score
from utils.helpers import point_in_rect


# Cached sub-surface for the title screen — allocated once, reused.
_title_temp_surface = None


def _get_title_temp_surface():
    global _title_temp_surface
    if (_title_temp_surface is None
            or _title_temp_surface.get_size() != (settings.WIDTH, settings.HEIGHT)):
        _title_temp_surface = pygame.Surface((settings.WIDTH, settings.HEIGHT))
    return _title_temp_surface


def draw_title_screen(surface, stars, time_elapsed, ox=0, oy=0):
    """Draw the ORBIT OVERDRIVE title screen, offset by (ox, oy) for screen shake.
    The whole screen (stars + text) shakes together."""
    temp = _get_title_temp_surface()
    _draw_title_content(temp, stars, time_elapsed)
    surface.blit(temp, (ox, oy))


def _draw_title_content(surface, stars, time_elapsed):
    """Render the title screen content to the given surface (no shake)."""
    surface.fill(BLACK)

    for star in stars:
        star[1] += star[2] * 0.5
        if star[1] > settings.HEIGHT:
            star[1] = 0
            star[0] = random.randint(0, settings.WIDTH)
        brightness = int(100 + star[2] * 50)
        color = (brightness, brightness, brightness)
        pygame.draw.circle(surface, color, (int(star[0]), int(star[1])), 1)

    cx = settings.WIDTH // 2
    high_score = load_high_score()
    last_score = load_last_score()

    # --- Top header: SCORE (last run) + HIGH SCORE, symmetric around cx ---
    label_font = get_font(20)
    value_font = get_font(28)

    score_label = label_font.render("SCORE", True, RED)
    score_value = value_font.render(f"{last_score:06d}", True, WHITE)
    high_label = label_font.render("HIGH SCORE", True, RED)
    high_value = value_font.render(f"{high_score:06d}", True, WHITE)

    gap = 60
    score_col_w = max(score_label.get_width(), score_value.get_width())
    score_col_x = cx - gap // 2 - score_col_w
    high_col_x = cx + gap // 2

    surface.blit(score_label, (score_col_x, 30))
    surface.blit(score_value, (score_col_x, 62))
    surface.blit(high_label, (high_col_x, 30))
    surface.blit(high_value, (high_col_x, 62))

    # --- Title block ---
    title_font_big = get_font(78)
    sub_font = get_font(20)
    start_font = get_font(30)
    studio_font = get_font(16)

    orbit_main = title_font_big.render("ORBIT", True, RED)
    overdrive_main = title_font_big.render("OVERDRIVE", True, RED)
    orbit_shadow = title_font_big.render("ORBIT", True, (80, 0, 0))
    overdrive_shadow = title_font_big.render("OVERDRIVE", True, (80, 0, 0))
    subtitle = sub_font.render("- TURBO EDITION -", True, GRAY)
    start_text = start_font.render("PRESS SPACE TO START", True, YELLOW)

    line_gap = 18
    block_height = (orbit_main.get_height() + overdrive_main.get_height()
                     + subtitle.get_height() + start_text.get_height()
                     + 3 * line_gap + 44)

    block_top = settings.HEIGHT // 2 - block_height // 2

    orbit_y = block_top
    overdrive_y = orbit_y + orbit_main.get_height() + line_gap
    subtitle_y = overdrive_y + overdrive_main.get_height() + line_gap
    start_y = subtitle_y + subtitle.get_height() + line_gap + 44

    surface.blit(orbit_shadow, (cx - orbit_shadow.get_width() // 2 + 4, orbit_y + 4))
    surface.blit(orbit_main, (cx - orbit_main.get_width() // 2, orbit_y))

    surface.blit(overdrive_shadow, (cx - overdrive_shadow.get_width() // 2 + 4, overdrive_y + 4))
    surface.blit(overdrive_main, (cx - overdrive_main.get_width() // 2, overdrive_y))

    surface.blit(subtitle, (cx - subtitle.get_width() // 2, subtitle_y))

    # --- Clickable start button ---
    # Build a rect for the "PRESS SPACE TO START" text. Blink as before,
    # but always draw so click hit-detection works even between blinks.
    sw = start_text.get_width()
    sh = start_text.get_height()
    # We need a stable rect across frames; use a slightly padded box.
    pad_x, pad_y = 30, 12
    start_rect = pygame.Rect(0, 0, sw + pad_x * 2, sh + pad_y * 2)
    start_rect.center = (cx, start_y + sh // 2)

    # Hover highlight
    mouse_pos = pygame.mouse.get_pos()
    hovered = point_in_rect(mouse_pos[0], mouse_pos[1], start_rect)

    if hovered:
        # Draw a filled highlight behind the text
        pygame.draw.rect(surface, (60, 60, 30), start_rect, border_radius=2)
        pygame.draw.rect(surface, YELLOW, start_rect, 2, border_radius=2)
        # Override text color on hover
        start_text = start_font.render("PRESS SPACE TO START", True, WHITE)
    else:
        blink = math.sin(time_elapsed * 3) > 0
        if not blink:
            # Dim on blink-off (but keep rect for hit detection) — this is
            # what actually makes it blink; same color as "on" would not.
            start_text = start_font.render("PRESS SPACE TO START", True, (90, 75, 0))

    surface.blit(start_text, start_text.get_rect(center=start_rect.center))

    # Cache the rect on the surface for click handling (using a module attr
    # is cleaner than stashing on the surface; we re-derive in main.py).

    studio_text = studio_font.render("WILD WINNERS STUDIO", True, GRAY)
    surface.blit(studio_text, (cx - studio_text.get_width() // 2, settings.HEIGHT - 45))


def get_title_start_rect():
    """Return the rect of the 'PRESS SPACE TO START' button on the title screen.
    Must match the layout in _draw_title_content exactly."""
    cx = settings.WIDTH // 2
    title_font_big = get_font(78)
    sub_font = get_font(20)
    start_font = get_font(30)
    start_text = start_font.render("PRESS SPACE TO START", True, YELLOW)
    orbit_main = title_font_big.render("ORBIT", True, RED)
    overdrive_main = title_font_big.render("OVERDRIVE", True, RED)
    subtitle = sub_font.render("- TURBO EDITION -", True, GRAY)

    line_gap = 18
    block_height = (orbit_main.get_height() + overdrive_main.get_height()
                     + subtitle.get_height() + start_text.get_height()
                     + 3 * line_gap + 44)
    block_top = settings.HEIGHT // 2 - block_height // 2
    orbit_y = block_top
    overdrive_y = orbit_y + orbit_main.get_height() + line_gap
    subtitle_y = overdrive_y + overdrive_main.get_height() + line_gap
    start_y = subtitle_y + subtitle.get_height() + line_gap + 44

    sw = start_text.get_width()
    sh = start_text.get_height()
    pad_x, pad_y = 30, 12
    rect = pygame.Rect(0, 0, sw + pad_x * 2, sh + pad_y * 2)
    rect.center = (cx, start_y + sh // 2)
    return rect