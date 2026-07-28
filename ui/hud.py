import math
import pygame
import settings
from settings import WHITE, RED, YELLOW, CYAN, GREEN, GRAY, DARK_GRAY
from utils.fonts import get_font
from utils.helpers import point_in_rect


def draw_hud(surface, score, high_score, lives):
    """Draw the in-game HUD: score, high score, lives."""

    label_font = get_font(18)
    value_font = get_font(30)

    # SCORE (top-left)
    score_label = label_font.render("SCORE", True, RED)
    surface.blit(score_label, (25, 20))
    score_value = value_font.render(f"{int(score):06d}", True, WHITE)
    surface.blit(score_value, (25, 52))

    # HIGH SCORE (top-right, right-aligned so it never overflows the edge)
    hs_label = label_font.render("HIGH SCORE", True, RED)
    surface.blit(hs_label, (settings.WIDTH - 25 - hs_label.get_width(), 20))
    hs_value = value_font.render(f"{int(high_score):06d}", True, WHITE)
    surface.blit(hs_value, (settings.WIDTH - 25 - hs_value.get_width(), 52))

    # --- Lives indicator (bottom-left) ---
    lives_label = get_font(18).render("LIVES", True, RED)
    surface.blit(lives_label, (25, settings.HEIGHT - 55))

    icon_x = 120
    icon_y = settings.HEIGHT - 38
    for i in range(lives):
        points = [
            (icon_x, icon_y),
            (icon_x - 10, icon_y + 15),
            (icon_x - 5, icon_y + 10),
            (icon_x, icon_y + 13),
            (icon_x + 5, icon_y + 10),
            (icon_x + 10, icon_y + 15),
        ]
        pygame.draw.polygon(surface, CYAN, points)
        pygame.draw.polygon(surface, WHITE, points, 1)
        icon_x += 28


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

    opt_font = get_font(22)
    mouse_pos = pygame.mouse.get_pos()

    # --- Retry button ---
    blink1 = math.sin(time_elapsed * 3) > 0
    retry_text = opt_font.render("PRESS SPACE TO RETRY", True, YELLOW)
    if not blink1:
        # Show it dimmer off-blink but still hit-testable
        retry_text_dim = opt_font.render("PRESS SPACE TO RETRY", True, (90, 90, 0))
        retry_text = retry_text_dim
    retry_rect = retry_text.get_rect(center=(cx, cy + 135))
    pad = 24
    retry_btn = pygame.Rect(0, 0, retry_rect.width + pad * 2, retry_rect.height + 12)
    retry_btn.center = retry_rect.center
    if point_in_rect(mouse_pos[0], mouse_pos[1], retry_btn):
        pygame.draw.rect(surface, (60, 60, 0), retry_btn, border_radius=3)
        pygame.draw.rect(surface, YELLOW, retry_btn, 2, border_radius=3)
        if blink1:
            retry_text = opt_font.render("PRESS SPACE TO RETRY", True, WHITE)
    surface.blit(retry_text, retry_text.get_rect(center=retry_btn.center))

    # --- Menu button ---
    menu_text = opt_font.render("PRESS M FOR MENU", True, CYAN)
    menu_rect = menu_text.get_rect(center=(cx, cy + 178))
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