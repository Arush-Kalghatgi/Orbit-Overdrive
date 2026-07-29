# rendering/touch_ui.py
#
# Touch UI rendering for Orbit Overdrive.
#
# Layout (matches the user's design sketch):
#   - Pause: top-LEFT corner
#   - Joystick: bottom-LEFT corner
#   - Boost: bottom-RIGHT area, upper position (closer to right corner)
#   - Shoot: bottom-RIGHT area, lower-LEFT of boost (diagonally arranged)
#            but fully within the screen (not cut off at the bottom)

import math
import pygame
import settings


# --- Layout constants (in pixels) ---
JOYSTICK_BASE_RADIUS = 75
JOYSTICK_KNOB_RADIUS = 35
SHOOT_BUTTON_RADIUS = 55
BOOST_BUTTON_RADIUS = 42
PAUSE_BUTTON_SIZE = 46
BUTTON_PADDING = 20
BUTTON_GAP = 18           # gap between adjacent buttons
BUTTON_PRESS_OFFSET = 4

# --- Color palette ---
JOYSTICK_BASE_COLOR = (45, 50, 60)
JOYSTICK_BASE_RIM = (25, 28, 35)
JOYSTICK_BASE_HIGHLIGHT = (75, 82, 95)
JOYSTICK_KNOB_COLOR = (90, 100, 115)
JOYSTICK_KNOB_HIGHLIGHT = (140, 152, 170)
JOYSTICK_KNOB_SHADOW = (50, 58, 70)

SHOOT_TOP = (220, 60, 60)
SHOOT_HIGHLIGHT = (255, 130, 130)
SHOOT_SHADOW = (140, 25, 25)
SHOOT_SIDE = (90, 15, 15)

BOOST_TOP = (60, 180, 230)
BOOST_HIGHLIGHT = (130, 220, 255)
BOOST_SHADOW = (25, 100, 150)
BOOST_SIDE = (15, 60, 90)

PAUSE_TOP = (200, 200, 215)
PAUSE_HIGHLIGHT = (240, 240, 250)
PAUSE_SHADOW = (120, 122, 135)
PAUSE_SIDE = (70, 72, 82)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_OUTLINE = (20, 20, 25)


def _draw_chunky_button(surface, rect, top_color, highlight_color,
                        shadow_color, side_color, pressed):
    ox = 0
    oy = 0
    top = top_color
    if pressed:
        oy = BUTTON_PRESS_OFFSET
        top = tuple(max(0, int(c * 0.75)) for c in top_color)

    cx = rect.centerx + ox
    cy = rect.centery + oy
    radius = rect.width // 2

    if not pressed:
        shadow_offset = 3
        shadow_rect = pygame.Rect(0, 0, rect.width, rect.height)
        shadow_rect.center = (cx + shadow_offset, cy + shadow_offset)
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height),
                                     pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 100), shadow_surf.get_rect())
        surface.blit(shadow_surf, shadow_rect.topleft)

    pygame.draw.circle(surface, side_color, (cx, cy), radius)

    top_radius = radius - 4
    pygame.draw.circle(surface, top, (cx, cy), top_radius)

    pygame.draw.circle(surface, highlight_color, (cx, cy), top_radius, 2)

    SHADOW_SURF = pygame.Surface((top_radius * 2 + 4, top_radius * 2 + 4),
                                 pygame.SRCALPHA)
    if SHADOW_SURF.get_width() > 0 and SHADOW_SURF.get_height() > 0:
        arc_rect = pygame.Rect(2, 2, top_radius * 2, top_radius * 2)
        pygame.draw.arc(SHADOW_SURF, (*shadow_color, 180),
                        arc_rect, math.radians(20), math.radians(160), 3)
        surface.blit(SHADOW_SURF, (cx - top_radius - 2, cy - top_radius - 2))

    pygame.draw.circle(surface, DARK_OUTLINE, (cx, cy), radius, 2)


def _draw_joystick(surface, center, base_radius, knob_radius,
                   knob_pos, pressed):
    cx, cy = center

    SHADOW = pygame.Surface((base_radius * 2 + 8, base_radius * 2 + 8),
                            pygame.SRCALPHA)
    pygame.draw.ellipse(SHADOW, (0, 0, 0, 120),
                        (4, 6, base_radius * 2, base_radius * 2))
    surface.blit(SHADOW, (cx - base_radius - 4, cy - base_radius - 4))

    pygame.draw.circle(surface, JOYSTICK_BASE_RIM, (cx, cy), base_radius)
    well_radius = base_radius - 4
    pygame.draw.circle(surface, JOYSTICK_BASE_COLOR, (cx, cy), well_radius)

    INNER_SHADOW = pygame.Surface((well_radius * 2 + 4, well_radius * 2 + 4),
                                  pygame.SRCALPHA)
    arc_rect = pygame.Rect(2, 2, well_radius * 2, well_radius * 2)
    pygame.draw.arc(INNER_SHADOW, (15, 18, 25, 200),
                    arc_rect, math.radians(180), math.radians(360), 3)
    surface.blit(INNER_SHADOW, (cx - well_radius - 2, cy - well_radius - 2))

    INNER_HL = pygame.Surface((well_radius * 2 + 4, well_radius * 2 + 4),
                              pygame.SRCALPHA)
    arc_rect = pygame.Rect(2, 2, well_radius * 2, well_radius * 2)
    pygame.draw.arc(INNER_HL, (*JOYSTICK_BASE_HIGHLIGHT, 120),
                    arc_rect, math.radians(0), math.radians(180), 2)
    surface.blit(INNER_HL, (cx - well_radius - 2, cy - well_radius - 2))

    if knob_pos is None:
        knob_cx, knob_cy = cx, cy
    else:
        knob_cx, knob_cy = knob_pos

    if knob_pos is not None and (knob_cx != cx or knob_cy != cy):
        KNOB_SHADOW = pygame.Surface((knob_radius * 2 + 6, knob_radius * 2 + 6),
                                     pygame.SRCALPHA)
        pygame.draw.ellipse(KNOB_SHADOW, (0, 0, 0, 100),
                            (3, 4, knob_radius * 2, knob_radius * 2))
        surface.blit(KNOB_SHADOW, (knob_cx - knob_radius - 3,
                                    knob_cy - knob_radius - 3))

    pygame.draw.circle(surface, JOYSTICK_KNOB_SHADOW,
                       (int(knob_cx), int(knob_cy)), knob_radius)

    top_radius = knob_radius - 3
    pygame.draw.circle(surface, JOYSTICK_KNOB_COLOR,
                       (int(knob_cx), int(knob_cy)), top_radius)

    KNOB_HL = pygame.Surface((top_radius * 2 + 4, top_radius * 2 + 4),
                             pygame.SRCALPHA)
    arc_rect = pygame.Rect(2, 2, top_radius * 2, top_radius * 2)
    pygame.draw.arc(KNOB_HL, (*JOYSTICK_KNOB_HIGHLIGHT, 220),
                    arc_rect, math.radians(180), math.radians(360), 2)
    surface.blit(KNOB_HL, (int(knob_cx) - top_radius - 2,
                            int(knob_cy) - top_radius - 2))

    KNOB_SH = pygame.Surface((top_radius * 2 + 4, top_radius * 2 + 4),
                             pygame.SRCALPHA)
    arc_rect = pygame.Rect(2, 2, top_radius * 2, top_radius * 2)
    pygame.draw.arc(KNOB_SH, (30, 36, 50, 180),
                    arc_rect, math.radians(0), math.radians(180), 2)
    surface.blit(KNOB_SH, (int(knob_cx) - top_radius - 2,
                            int(knob_cy) - top_radius - 2))

    pygame.draw.circle(surface, DARK_OUTLINE,
                       (int(knob_cx), int(knob_cy)), knob_radius, 1)


def _draw_pause_button(surface, rect, pressed):
    ox = 0
    oy = 0
    top = PAUSE_TOP
    if pressed:
        oy = BUTTON_PRESS_OFFSET
        top = tuple(max(0, int(c * 0.75)) for c in PAUSE_TOP)

    cx = rect.centerx + ox
    cy = rect.centery + oy
    size = rect.width
    half = size // 2

    if not pressed:
        shadow_rect = pygame.Rect(0, 0, size, size)
        shadow_rect.center = (cx + 3, cy + 3)
        shadow_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 100), shadow_surf.get_rect(),
                         border_radius=4)
        surface.blit(shadow_surf, shadow_rect.topleft)

    side_rect = pygame.Rect(cx - half, cy - half, size, size)
    pygame.draw.rect(surface, PAUSE_SIDE, side_rect, border_radius=6)

    top_inset = 4
    top_rect = pygame.Rect(cx - half + top_inset, cy - half + top_inset,
                           size - top_inset * 2, size - top_inset * 2)
    pygame.draw.rect(surface, top, top_rect, border_radius=4)

    line_x_left = cx - 8
    line_x_right = cx + 8
    line_top = cy - 8
    line_bot = cy + 8
    line_w = 3
    pygame.draw.rect(surface, PAUSE_SIDE,
                     (line_x_left - line_w // 2, line_top, line_w, line_bot - line_top))
    pygame.draw.rect(surface, PAUSE_SIDE,
                     (line_x_right - line_w // 2, line_top, line_w, line_bot - line_top))

    pygame.draw.rect(surface, DARK_OUTLINE, side_rect, 2, border_radius=6)


def draw_touch_ui(surface, input_manager, time_elapsed=0.0):
    """Draw all on-screen touch UI elements.

    Layout (matches the user's design sketch):
      - Pause: top-LEFT corner
      - Joystick: bottom-LEFT corner
      - Boost: bottom-RIGHT area, upper position
      - Shoot: bottom-RIGHT area, lower-LEFT of boost (diagonally arranged)
    """
    W = settings.WIDTH
    H = settings.HEIGHT

    # --- Joystick: bottom-left corner ---
    joystick_center = (BUTTON_PADDING + JOYSTICK_BASE_RADIUS,
                       H - BUTTON_PADDING - JOYSTICK_BASE_RADIUS)
    joystick_base_rect = pygame.Rect(
        joystick_center[0] - JOYSTICK_BASE_RADIUS,
        joystick_center[1] - JOYSTICK_BASE_RADIUS,
        JOYSTICK_BASE_RADIUS * 2,
        JOYSTICK_BASE_RADIUS * 2
    )

    # --- Boost button: upper position in the bottom-RIGHT area ---
    # Positioned so that BOTH boost and shoot fit fully on screen.
    # The diagonal offset between them is BOOST_RADIUS + SHOOT_RADIUS + GAP.
    DIAGONAL_OFFSET = BOOST_BUTTON_RADIUS + SHOOT_BUTTON_RADIUS + BUTTON_GAP  # 115

    # Boost is anchored to the right edge. Its center y is computed so that
    # boost + diagonal_offset down to shoot + shoot_radius + bottom padding
    # still fits within the screen.
    boost_center_x = W - BUTTON_PADDING - BOOST_BUTTON_RADIUS
    # The maximum y for boost center, given the diagonal: shoot needs to be
    # at y = boost_y + DIAGONAL_OFFSET, and shoot's bottom (y + radius)
    # must be <= H - BUTTON_PADDING. So boost_y <= H - BUTTON_PADDING -
    # SHOOT_RADIUS - DIAGONAL_OFFSET.
    boost_center_y = H - BUTTON_PADDING - SHOOT_BUTTON_RADIUS - DIAGONAL_OFFSET
    boost_rect = pygame.Rect(
        boost_center_x - BOOST_BUTTON_RADIUS,
        boost_center_y - BOOST_BUTTON_RADIUS,
        BOOST_BUTTON_RADIUS * 2,
        BOOST_BUTTON_RADIUS * 2
    )

    # --- Shoot button: lower-LEFT of boost (diagonally arranged) ---
    # shoot center is at (boost_x - DIAGONAL_OFFSET, boost_y + DIAGONAL_OFFSET)
    shoot_center_x = boost_center_x - DIAGONAL_OFFSET
    shoot_center_y = boost_center_y + DIAGONAL_OFFSET
    # Make sure shoot stays on-screen horizontally
    if shoot_center_x - SHOOT_BUTTON_RADIUS < BUTTON_PADDING:
        shoot_center_x = SHOOT_BUTTON_RADIUS + BUTTON_PADDING
    shoot_rect = pygame.Rect(
        shoot_center_x - SHOOT_BUTTON_RADIUS,
        shoot_center_y - SHOOT_BUTTON_RADIUS,
        SHOOT_BUTTON_RADIUS * 2,
        SHOOT_BUTTON_RADIUS * 2
    )

    # --- Pause button: top-LEFT corner ---
    pause_size = PAUSE_BUTTON_SIZE
    pause_rect = pygame.Rect(
        BUTTON_PADDING,
        BUTTON_PADDING,
        pause_size,
        pause_size
    )

    input_manager.set_layout(
        joystick_base_rect,
        input_manager.joystick_knob_pos,
        shoot_rect,
        boost_rect,
        pause_rect,
    )

    # --- Draw elements ---
    _draw_joystick(surface, joystick_center, JOYSTICK_BASE_RADIUS,
                   JOYSTICK_KNOB_RADIUS, input_manager.joystick_knob_pos,
                   input_manager._joystick_finger != -1)

    # Boost drawn first (so the visual order matches the diagonal)
    _draw_chunky_button(surface, boost_rect, BOOST_TOP, BOOST_HIGHLIGHT,
                        BOOST_SHADOW, BOOST_SIDE, input_manager.boost_pressed)
    _draw_lightning_icon(surface, boost_rect, pressed=input_manager.boost_pressed)

    _draw_chunky_button(surface, shoot_rect, SHOOT_TOP, SHOOT_HIGHLIGHT,
                        SHOOT_SHADOW, SHOOT_SIDE, input_manager.shoot_pressed)
    _draw_crosshair_icon(surface, shoot_rect, pressed=input_manager.shoot_pressed)

    _draw_pause_button(surface, pause_rect, input_manager._pause_finger != -1)

    return {
        "joystick": joystick_base_rect,
        "shoot": shoot_rect,
        "boost": boost_rect,
        "pause": pause_rect,
    }


def _draw_lightning_icon(surface, rect, pressed):
    oy = BUTTON_PRESS_OFFSET if pressed else 0
    cx = rect.centerx
    cy = rect.centery + oy
    r = 12
    points = [
        (cx - 2, cy - r),
        (cx + 5, cy - r + 2),
        (cx + 1, cy - 1),
        (cx + 7, cy - 1),
        (cx - 1, cy + r),
        (cx - 4, cy + 1),
        (cx, cy - r + 4),
        (cx - 6, cy - r + 2),
    ]
    pygame.draw.polygon(surface, WHITE, points)
    pygame.draw.polygon(surface, BOOST_SIDE, points, 1)


def _draw_crosshair_icon(surface, rect, pressed):
    oy = BUTTON_PRESS_OFFSET if pressed else 0
    cx = rect.centerx
    cy = rect.centery + oy
    r = 10
    pygame.draw.circle(surface, WHITE, (cx, cy), r, 2)
    pygame.draw.line(surface, WHITE, (cx - r - 3, cy), (cx - r + 4, cy), 2)
    pygame.draw.line(surface, WHITE, (cx + r - 4, cy), (cx + r + 3, cy), 2)
    pygame.draw.line(surface, WHITE, (cx, cy - r - 3), (cx, cy - r + 4), 2)
    pygame.draw.line(surface, WHITE, (cx, cy + r - 4), (cx, cy + r + 3), 2)
    pygame.draw.circle(surface, WHITE, (cx, cy), 2)
