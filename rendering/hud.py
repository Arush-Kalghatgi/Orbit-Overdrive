import math
import pygame
import settings
from settings import WHITE, RED, YELLOW, CYAN, GREEN, GRAY, DARK_GRAY
from utils.fonts import get_font
from utils.helpers import point_in_rect


def draw_fuel_bar(surface, x, y, fuel, max_fuel, width=230, height=18):
    """Draw the turbo fuel bar with a 'TURBO' label."""
    label = get_font(20).render("TURBO", True, WHITE)
    surface.blit(label, (x, y))

    bar_x = x
    bar_y = y + 28
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


def draw_hud(surface, score, lives):
    """Draw the in-game HUD in the top-right area.

    Order (top to bottom):
      - TURBO fuel bar (at the very top)
      - SCORE label + value
      - LIVES label + triangles (at the bottom of the HUD)

    All elements are right-aligned. No high score is shown here.
    """
    label_font = get_font(18)
    value_font = get_font(30)

    right_margin = 25
    bar_width = 230

    # --- TURBO FUEL BAR (at the top, right-aligned) ---
    from entities import boost as boost_state
    bar_x = settings.WIDTH - right_margin - bar_width
    bar_y = 20
    draw_fuel_bar(surface, bar_x, bar_y, boost_state.boost_fuel, boost_state.MAX_FUEL,
                  width=bar_width)

    # --- SCORE (below the turbo bar) ---
    # Turbo bar: label at y=20, bar at y=48, bar ends at y=66. So SCORE
    # label starts at y=85 to give a clear gap.
    score_label = label_font.render("SCORE", True, RED)
    score_value = value_font.render(f"{int(score):06d}", True, WHITE)

    score_label_x = settings.WIDTH - right_margin - score_label.get_width()
    score_value_x = settings.WIDTH - right_margin - score_value.get_width()
    surface.blit(score_label, (score_label_x, 100))
    surface.blit(score_value, (score_value_x, 132))

    # --- LIVES (below the score) ---
    # Score value ends at ~y=168. LIVES label at y=200, triangles at y=220.
    lives_label_y = 200
    lives_label = label_font.render("LIVES", True, RED)
    surface.blit(lives_label,
                 (settings.WIDTH - right_margin - lives_label.get_width(), lives_label_y))

    icon_size = 28
    icon_baseline_y = 235
    rightmost_center_x = settings.WIDTH - right_margin - 10
    for i in range(lives - 1, -1, -1):
        cx = rightmost_center_x - i * icon_size
        points = [
            (cx, icon_baseline_y - 15),
            (cx - 10, icon_baseline_y),
            (cx - 5, icon_baseline_y - 5),
            (cx, icon_baseline_y - 2),
            (cx + 5, icon_baseline_y - 5),
            (cx + 10, icon_baseline_y),
        ]
        pygame.draw.polygon(surface, CYAN, points)
        pygame.draw.polygon(surface, WHITE, points, 1)


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
