# rendering/hud.py
#
# In-game HUD:
#   - Bottom-left:  OVERDRIVE fuel bar + LIVES shields
#   - Bottom-right: SCORE (live) + HIGH SCORE (catches up mid-game + blinks)
#
# High score behavior (Option C):
#   - HUD displays max(pre_run_high_score, current_score)
#   - When current score first crosses pre_run_high_score, HIGH display
#     blinks once (3 quick flashes) then settles into "following" mode.

import math
import pygame
import settings
from settings import WHITE, RED, YELLOW, CYAN, GREEN, GRAY, DARK_GRAY, BLUE
from utils.fonts import get_font
from utils.helpers import point_in_rect


# ============================================================
# Per-run high-score blink tracking
# ============================================================
_blinked_this_run = False
_pre_run_high = 0
_blink_timer = 0.0


def reset_high_score_state(pre_run_high):
    global _blinked_this_run, _pre_run_high, _blink_timer
    _pre_run_high = int(pre_run_high)
    _blinked_this_run = False
    _blink_timer = 0.0


def update_hud_animation(dt):
    global _blink_timer
    if _blink_timer > 0.0:
        _blink_timer = max(0.0, _blink_timer - dt)


# ============================================================
# Shield shape — pixel-art style, vertical-hexagon with notch at top
# ============================================================
def _shield_points(cx, cy, size=20):
    """Return polygon points for a stylized sci-fi shield centered at
    (cx, cy). size = full height in pixels (default 20).
    Shape: hex with a V-notch cut into the top edge, point at the
    bottom. Reads as 'shield' from a few feet away."""
    s = size
    h = s // 2
    pts = [
        (cx - h + 2, cy - s // 2 + 4),    # upper-left, just below notch
        (cx - h,     cy - s // 2 + 8),    # left corner
        (cx - h,     cy + 2),             # left mid
        (cx - h + 4, cy + s // 2 - 2),    # lower-left
        (cx,         cy + s // 2),        # bottom point
        (cx + h - 4, cy + s // 2 - 2),    # lower-right
        (cx + h,     cy + 2),             # right mid
        (cx + h,     cy - s // 2 + 8),    # right corner
        (cx + h - 2, cy - s // 2 + 4),    # upper-right, just below notch
        (cx + 2,     cy - 4),             # right side of notch dip
        (cx,         cy - s // 2),        # notch bottom (V cut)
        (cx - 2,     cy - 4),             # left side of notch dip
    ]
    return pts


def _draw_lives(surface, lives, x, y):
    """Draw 'LIVES' label + cyan hex shields, left-aligned at (x, y).

    Each shield has a cyan body, blue inner highlight band, and white
    outline. They're drawn left-to-right with consistent spacing.
    """
    label_font = get_font(18)
    label = label_font.render("LIVES", True, RED)
    surface.blit(label, (x, y))

    shield_height = 24
    shield_spacing = 34   # horizontal gap between shields
    icon_baseline_y = y + 44   # extra padding so shields don't clip

    for i in range(lives):
        shield_cx = x + i * shield_spacing + shield_height // 2
        shield_cy = icon_baseline_y - shield_height // 2

        pts = _shield_points(shield_cx, shield_cy, size=shield_height)

        # Outer body — cyan
        pygame.draw.polygon(surface, CYAN, pts)
        # Blue inner highlight band (smaller polygon offset inward)
        inset = 3
        h = shield_height // 2 - inset
        inner_pts = [
            (shield_cx - h + 1, shield_cy - shield_height // 2 + inset + 2),
            (shield_cx - h,     shield_cy - shield_height // 2 + inset + 6),
            (shield_cx - h,     shield_cy + inset - 2),
            (shield_cx - h + 3, shield_cy + shield_height // 2 - inset - 2),
            (shield_cx,         shield_cy + shield_height // 2 - inset),
            (shield_cx + h - 3, shield_cy + shield_height // 2 - inset - 2),
            (shield_cx + h,     shield_cy + inset - 2),
            (shield_cx + h,     shield_cy - shield_height // 2 + inset + 6),
            (shield_cx + h - 1, shield_cy - shield_height // 2 + inset + 2),
            (shield_cx + 2,     shield_cy - inset),
            (shield_cx,         shield_cy - shield_height // 2 + 1),
            (shield_cx - 2,     shield_cy - inset),
        ]
        pygame.draw.polygon(surface, BLUE, inner_pts)

        # White outline on top so the shield reads clearly
        pygame.draw.polygon(surface, WHITE, pts, 1)


def _draw_overdrive(surface, x, y, fuel, max_fuel, width=240, height=18):
    """Draw 'OVERDRIVE' label + colored fuel bar at (x, y)."""
    label_font = get_font(18)
    label = label_font.render("OVERDRIVE", True, WHITE)
    surface.blit(label, (x, y))

    bar_x = x
    bar_y = y + 24
    pygame.draw.rect(surface, DARK_GRAY, (bar_x, bar_y, width, height))

    fill_ratio = fuel / max_fuel if max_fuel > 0 else 0
    fill_width = int(width * fill_ratio)

    if fill_ratio > 0.5:
        color = CYAN
    elif fill_ratio > 0.25:
        color = YELLOW
    else:
        color = RED

    pygame.draw.rect(surface, color, (bar_x, bar_y, fill_width, height))
    pygame.draw.rect(surface, WHITE, (bar_x, bar_y, width, height), 1)


def _draw_score_block(surface, score, x, y, color=WHITE):
    """Draw 'SCORE' label + 6-digit value, right-aligned at (x, y)."""
    label_font = get_font(18)
    value_font = get_font(28)

    label = label_font.render("SCORE", True, RED)
    value = value_font.render(f"{int(score):06d}", True, color)

    label_x = x - label.get_width()
    value_x = x - value.get_width()
    surface.blit(label, (label_x, y))
    surface.blit(value, (value_x, y + 22))


def _draw_high_score_block(surface, displayed_high, x, y):
    """Draw 'HIGH SCORE' label + 6-digit value, right-aligned at (x, y)."""
    label_font = get_font(16)
    value_font = get_font(28)

    in_blink = _blink_timer > 0.0
    if in_blink:
        phase = (_blink_timer / 0.9) * math.pi * 2 * 3
        flashing = math.sin(phase) > 0
        value_color = YELLOW if flashing else WHITE
        label_color = YELLOW
    else:
        value_color = WHITE
        label_color = GRAY

    label = label_font.render("HIGH SCORE", True, label_color)
    value = value_font.render(f"{int(displayed_high):06d}", True, value_color)

    label_x = x - label.get_width()
    value_x = x - value.get_width()
    surface.blit(label, (label_x, y))
    surface.blit(value, (value_x, y + 22))


def draw_hud(surface, score, lives, pre_run_high_score):
    """Draw the full in-game HUD.

    Bottom-left:  OVERDRIVE + LIVES (shields)
    Bottom-right: SCORE + HIGH SCORE (follows current if exceeded)
    """
    global _blinked_this_run, _blink_timer

    from entities import boost as boost_state

    H = settings.HEIGHT
    W = settings.WIDTH

    # Layout anchor: bottom edge of HUD block.
    # The shield's lowest point is icon_baseline_y + shield_height // 2.
    # We want the shield's bottom to sit 18px above the screen edge,
    # so we set the LIVES label position based on that.
    margin_x = 25
    bottom_margin = 18          # space between HUD bottom and screen edge
    row_gap = 60                # vertical gap between OVERDRIVE row and LIVES row
    shield_height = 24

    # y of the LIVES label (text baseline of the LIVES word)
    lives_label_y = H - bottom_margin - shield_height - 6  # shield bottom = label_y + shield_height + 6
    # Equivalent: the shield's center sits at label_y + shield_height // 2 + 6
    # and the shield's bottom sits at label_y + shield_height + 6.
    # That means shield bottom = H - bottom_margin. ✓

    overdrive_label_y = lives_label_y - row_gap

    # ============================================================
    # BOTTOM-LEFT: OVERDRIVE (top) + LIVES (bottom)
    # ============================================================
    left_x = margin_x
    _draw_overdrive(surface, left_x, overdrive_label_y,
                    boost_state.boost_fuel, boost_state.MAX_FUEL,
                    width=240)
    _draw_lives(surface, lives, left_x, lives_label_y)

    # ============================================================
    # BOTTOM-RIGHT: SCORE (top) + HIGH SCORE (bottom)
    # ============================================================
    right_x = W - margin_x
    high_label_y = lives_label_y
    score_label_y = overdrive_label_y

    cur_score = int(score)
    if cur_score > _pre_run_high:
        displayed_high = cur_score
        if not _blinked_this_run and _pre_run_high > 0:
            _blinked_this_run = True
            _blink_timer = 0.9
    else:
        displayed_high = _pre_run_high

    _draw_score_block(surface, cur_score, right_x, score_label_y, color=WHITE)
    _draw_high_score_block(surface, displayed_high, right_x, high_label_y)


def draw_game_over(surface, score, high_score, is_new_high, time_elapsed):
    """Draw the game over screen with clickable options."""
    cx = settings.WIDTH // 2
    cy = settings.HEIGHT // 2

    go_font = get_font(70)
    go_shadow = go_font.render("GAME OVER", True, (80, 0, 0))
    go_main = go_font.render("GAME OVER", True, RED)
    surface.blit(go_shadow, (cx - go_shadow.get_width() // 2 + 4, cy - 125 + 4))
    surface.blit(go_main, (cx - go_main.get_width() // 2, cy - 125))

    if is_new_high:
        banner_font = get_font(30)
        banner_shadow = banner_font.render("NEW HIGH SCORE!", True, (100, 80, 0))
        banner_main = banner_font.render("NEW HIGH SCORE!", True, YELLOW)
        surface.blit(banner_shadow, (cx - banner_shadow.get_width() // 2 + 2, cy - 15 + 2))
        surface.blit(banner_main, (cx - banner_main.get_width() // 2, cy - 15))

    final_label = get_font(18).render("FINAL SCORE", True, GRAY)
    surface.blit(final_label, (cx - final_label.get_width() // 2, cy + 25))
    final_score = get_font(44).render(f"{int(score):06d}", True, WHITE)
    surface.blit(final_score, (cx - final_score.get_width() // 2, cy + 52))

    high_label = get_font(16).render(f"HIGH SCORE: {int(high_score):06d}", True, GRAY)
    surface.blit(high_label, (cx - high_label.get_width() // 2, cy + 110))

    opt_font = get_font(22)
    mouse_pos = pygame.mouse.get_pos()

    blink1 = math.sin(time_elapsed * 3) > 0
    retry_text = opt_font.render("PRESS SPACE TO RETRY", True, YELLOW)
    if not blink1:
        retry_text = opt_font.render("PRESS SPACE TO RETRY", True, (90, 90, 0))
    retry_rect = retry_text.get_rect(center=(cx, cy + 165))
    pad = 24
    retry_btn = pygame.Rect(0, 0, retry_rect.width + pad * 2, retry_rect.height + 12)
    retry_btn.center = retry_rect.center
    if point_in_rect(mouse_pos[0], mouse_pos[1], retry_btn):
        pygame.draw.rect(surface, (60, 60, 0), retry_btn, border_radius=3)
        pygame.draw.rect(surface, YELLOW, retry_btn, 2, border_radius=3)
        if blink1:
            retry_text = opt_font.render("PRESS SPACE TO RETRY", True, WHITE)
    surface.blit(retry_text, retry_text.get_rect(center=retry_btn.center))

    menu_text = opt_font.render("PRESS M FOR MENU", True, CYAN)
    menu_rect = menu_text.get_rect(center=(cx, cy + 210))
    menu_btn = pygame.Rect(0, 0, menu_rect.width + pad * 2, menu_rect.height + 12)
    menu_btn.center = menu_rect.center
    if point_in_rect(mouse_pos[0], mouse_pos[1], menu_btn):
        pygame.draw.rect(surface, (0, 50, 60), menu_btn, border_radius=3)
        pygame.draw.rect(surface, CYAN, menu_btn, 2, border_radius=3)
        menu_text = opt_font.render("PRESS M FOR MENU", True, WHITE)
    surface.blit(menu_text, menu_text.get_rect(center=menu_btn.center))

    return {
        "retry": retry_btn,
        "menu": menu_btn,
    }
