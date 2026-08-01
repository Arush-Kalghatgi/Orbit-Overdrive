# rendering/help.py
#
# In-game "How to Play" overlay for desktop builds.
#
# Triggered by the "?" button (bottom-right) on title and pause screens.
# Two side-by-side panels on wide screens, stacked on narrow.

import pygame
import settings
from settings import (
    WHITE, GRAY, YELLOW, CYAN, GREEN, RED, BLACK, DARK_GRAY,
    DARK_BROWN, MEDIUM_GRAY, ORANGE,
)
from utils.fonts import get_font
from utils.helpers import point_in_rect


_BUTTON_SIZE = 46
_BUTTON_PADDING = 20

_HELP_TOP = (200, 200, 215)
_HELP_HIGHLIGHT = (240, 240, 250)
_HELP_SHADOW = (120, 122, 135)
_HELP_SIDE = (70, 72, 82)
_DARK_OUTLINE = (20, 20, 25)


def get_button_rect():
    return pygame.Rect(
        settings.WIDTH - _BUTTON_PADDING - _BUTTON_SIZE,
        settings.HEIGHT - _BUTTON_PADDING - _BUTTON_SIZE,
        _BUTTON_SIZE,
        _BUTTON_SIZE,
    )


def draw_button(surface, mouse_pos=None):
    rect = get_button_rect()
    cx, cy = rect.centerx, rect.centery
    size = rect.width
    half = size // 2

    shadow_rect = pygame.Rect(0, 0, size, size)
    shadow_rect.center = (cx + 3, cy + 3)
    shadow_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, (0, 0, 0, 100), shadow_surf.get_rect(),
                     border_radius=4)
    surface.blit(shadow_surf, shadow_rect.topleft)

    side_rect = pygame.Rect(cx - half, cy - half, size, size)
    pygame.draw.rect(surface, _HELP_SIDE, side_rect, border_radius=6)
    top_inset = 4
    top_rect = pygame.Rect(cx - half + top_inset, cy - half + top_inset,
                           size - top_inset * 2, size - top_inset * 2)
    pygame.draw.rect(surface, _HELP_TOP, top_rect, border_radius=4)

    if mouse_pos is not None and point_in_rect(mouse_pos[0], mouse_pos[1], rect):
        pygame.draw.rect(surface, WHITE, top_rect, 2, border_radius=4)

    glyph_font = get_font(28)
    glyph = glyph_font.render("?", True, _HELP_SIDE)
    glyph_rect = glyph.get_rect(center=(cx, cy + 2))
    surface.blit(glyph, glyph_rect)

    pygame.draw.rect(surface, _DARK_OUTLINE, side_rect, 2, border_radius=6)


_CONTROLS = [
    ("h1", "CONTROLS", CYAN),
    ("row", "MOVE",       "ARROWS / WASD",  WHITE),
    ("row", "SHOOT",      "SPACE",          WHITE),
    ("row", "BOOST",      "SHIFT",          WHITE),
    ("row", "PAUSE",      "ESC",            WHITE),
    ("row", "FULLSCREEN", "F11",            WHITE),
]

_SCORING = [
    ("h1", "SCORING", YELLOW),
    ("h2", "Points", WHITE),
    ("row", "BROWN ASTEROID",  "10 PTS",   DARK_BROWN),
    ("row", "GRAY ASTEROID",   "20 PTS",   MEDIUM_GRAY),
    ("row", "DARK ASTEROID",   "30 PTS",   GRAY),
    ("row", "TURBO PICKUP",    "+25 PTS",  CYAN),
    ("row", "LIFE PICKUP",     "+1 LIFE",  ORANGE),
    ("h2", "Turbo Boost", CYAN),
    ("bullet", "Hold SHIFT (or boost button) to activate", WHITE),
    ("bullet", "Drains 1 fuel per second", WHITE),
    ("bullet", "World moves 3x faster", WHITE),
    ("bullet", "Passive score gain x4", WHITE),
    ("bullet", "Per-kill score x2", WHITE),
    ("h2", "Lives", RED),
    ("bullet", "Start with 3 lives", WHITE),
    ("bullet", "A life pickup drops every 2-3 turbo pickups", WHITE),
    ("bullet", "Only drops if lives are below 3", WHITE),
]


_scroll_controls = 0.0
_scroll_scoring = 0.0
_max_scroll = {"controls": 0.0, "scoring": 0.0}

_drag_panel = None
_drag_start_y = 0
_drag_start_scroll = 0.0


def _layout_panels():
    W = settings.WIDTH
    H = settings.HEIGHT
    margin = 30
    header_h = 80
    footer_h = 60

    inner_w = W - margin * 2
    inner_h = H - margin * 2 - header_h - footer_h

    stacked = W < 800

    if stacked:
        panel_w = inner_w
        panel_h = (inner_h - 20) // 2
        controls = pygame.Rect(margin, margin + header_h, panel_w, panel_h)
        scoring = pygame.Rect(margin, margin + header_h + panel_h + 20,
                              panel_w, panel_h)
    else:
        panel_w = (inner_w - 30) // 2
        controls = pygame.Rect(margin, margin + header_h, panel_w, inner_h)
        scoring = pygame.Rect(margin + panel_w + 30, margin + header_h,
                              panel_w, inner_h)

    return {
        "controls": controls,
        "scoring": scoring,
    }, stacked


def _draw_panel(surface, panel_rect, rows, scroll, scroll_key):
    bg = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 200))
    surface.blit(bg, panel_rect.topleft)
    pygame.draw.rect(surface, WHITE, panel_rect, 2, border_radius=6)

    pad = 16
    inner = pygame.Rect(
        panel_rect.x + pad,
        panel_rect.y + pad,
        panel_rect.width - pad * 2,
        panel_rect.height - pad * 2,
    )

    prev_clip = surface.get_clip()
    surface.set_clip(inner)

    y = inner.y - scroll

    for row_tuple in rows:
        kind = row_tuple[0]
        if kind == "h1":
            _, text, color = row_tuple
            font = get_font(22)
            surf = font.render(text, True, color)
            x = inner.x + (inner.width - surf.get_width()) // 2
            surface.blit(surf, (x, y))
            y += 36
        elif kind == "h2":
            _, text, color = row_tuple
            font = get_font(18)
            surf = font.render(text, True, color)
            surface.blit(surf, (inner.x, y))
            y += 26
        elif kind == "bullet":
            _, text, color = row_tuple
            font = get_font(13)
            bullet_surf = font.render("-", True, color)
            surface.blit(bullet_surf, (inner.x + 6, y))
            text_surf = font.render(text, True, color)
            surface.blit(text_surf, (inner.x + 22, y))
            y += 22
        elif kind == "row":
            _, label_text, badge_text, badge_color = row_tuple
            label_font = get_font(14)
            label_surf = label_font.render(label_text, True, WHITE)
            badge_font = get_font(14)
            badge_surf = badge_font.render(badge_text, True, BLACK)
            badge_pad_x, badge_pad_y = 8, 4
            badge_w = badge_surf.get_width() + badge_pad_x * 2
            badge_h = badge_surf.get_height() + badge_pad_y * 2
            badge_rect = pygame.Rect(
                inner.right - badge_w, y - 2, badge_w, badge_h
            )
            pygame.draw.rect(surface, badge_color, badge_rect, border_radius=3)
            pygame.draw.rect(surface, WHITE, badge_rect, 1, border_radius=3)
            surface.blit(badge_surf,
                         (badge_rect.x + badge_pad_x, badge_rect.y + badge_pad_y))
            surface.blit(label_surf,
                         (inner.x, y + (badge_h - label_surf.get_height()) // 2))
            y += max(badge_h + 4, 28)

    surface.set_clip(prev_clip)

    total_h = y - (inner.y - scroll)
    _max_scroll[scroll_key] = max(0.0, total_h - inner.height)

    if _max_scroll[scroll_key] > 0:
        track_x = panel_rect.right - 8
        track_y = panel_rect.y + 8
        track_h = panel_rect.height - 16
        pygame.draw.rect(surface, DARK_GRAY,
                         (track_x, track_y, 4, track_h), border_radius=2)
        ratio = inner.height / max(total_h, 1)
        thumb_h = max(20, int(track_h * min(ratio, 1.0)))
        scroll_pos = scroll / _max_scroll[scroll_key] if _max_scroll[scroll_key] else 0
        thumb_y = track_y + int((track_h - thumb_h) * scroll_pos)
        pygame.draw.rect(surface, WHITE,
                         (track_x, thumb_y, 4, thumb_h), border_radius=2)


def draw_overlay(surface):
    overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT))
    overlay.set_alpha(220)
    overlay.fill(BLACK)
    surface.blit(overlay, (0, 0))

    title_font = get_font(44)
    title = title_font.render("HOW TO PLAY", True, YELLOW)
    title_x = (settings.WIDTH - title.get_width()) // 2
    surface.blit(title, (title_x, 30))

    panels, _ = _layout_panels()

    _draw_panel(surface, panels["controls"], _CONTROLS,
                _scroll_controls, "controls")
    _draw_panel(surface, panels["scoring"], _SCORING,
                _scroll_scoring, "scoring")

    hint_font = get_font(16)
    hint = hint_font.render("PRESS ESC OR CLICK OUTSIDE TO CLOSE", True, GRAY)
    return panels


def _panel_at_point(pos, panels):
    for key, rect in panels.items():
        if rect.collidepoint(pos):
            return key
    return None


def handle_events(events, mouse_pos, left_held):
    global _scroll_controls, _scroll_scoring
    global _drag_panel, _drag_start_y, _drag_start_scroll

    for event in events:
        if event.type == pygame.MOUSEWHEEL:
            panels, _ = _layout_panels()
            panel_key = _panel_at_point(mouse_pos, panels) or "controls"
            if panel_key == "controls":
                _scroll_controls = max(
                    0.0,
                    min(_scroll_controls - event.y * 30, _max_scroll["controls"]),
                )
            else:
                _scroll_scoring = max(
                    0.0,
                    min(_scroll_scoring - event.y * 30, _max_scroll["scoring"]),
                )

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            panels, _ = _layout_panels()
            if _panel_at_point(mouse_pos, panels) is None:
                _drag_panel = None
                return "close"
            panel_key = _panel_at_point(mouse_pos, panels)
            _drag_panel = panel_key
            _drag_start_y = mouse_pos[1]
            _drag_start_scroll = (
                _scroll_controls if panel_key == "controls" else _scroll_scoring
            )

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            _drag_panel = None

    if _drag_panel is not None:
        cur_y = mouse_pos[1]
        if _drag_panel == "controls":
            new_scroll = _drag_start_scroll + (_drag_start_y - cur_y)
            _scroll_controls = max(0.0, min(new_scroll, _max_scroll["controls"]))
        else:
            new_scroll = _drag_start_scroll + (_drag_start_y - cur_y)
            _scroll_scoring = max(0.0, min(new_scroll, _max_scroll["scoring"]))

    return None


def reset_scroll():
    global _scroll_controls, _scroll_scoring
    _scroll_controls = 0.0
    _scroll_scoring = 0.0
