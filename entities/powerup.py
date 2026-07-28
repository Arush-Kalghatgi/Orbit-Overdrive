import pygame
import math
import random
import settings
from settings import CYAN, WHITE, BLACK, LIGHT_BLUE


class TurboPickup(pygame.Rect):
    SIZE = 32
    SPEED = 3.0  # Faster than red asteroids (1.5-2.3), slower than gray (2.5-3.5+)

    def __init__(self, x, y):
        super().__init__(x, y, self.SIZE, self.SIZE)
        self.speed = self.SPEED
        self.pulse = random.uniform(0, 6.28)

    def update_with_dt(self, dt):
        self.y += self.speed * dt * 60
        self.pulse += dt * 3
        return self.y < settings.HEIGHT


class LifePickup(pygame.Rect):
    """Extra-life pickup: gold circle with a wrench + screwdriver in an X."""
    SIZE = 32
    SPEED = 3.0  # Same tier as TurboPickup for visual consistency

    def __init__(self, x, y):
        super().__init__(x, y, self.SIZE, self.SIZE)
        self.speed = self.SPEED
        self.pulse = random.uniform(0, 6.28)

    def update_with_dt(self, dt):
        self.y += self.speed * dt * 60
        self.pulse += dt * 3
        return self.y < settings.HEIGHT



def _lightning_points(cx, cy, size):
    """Bigger, more visible lightning bolt."""
    s = size
    return [
        (cx + 0,  cy - s),        # top
        (cx + 6,  cy - s + 3),    # upper right
        (cx + 1,  cy - 2),        # middle bend
        (cx + 6,  cy - 2),        # right notch
        (cx + 0,  cy + s),        # bottom
        (cx - 6,  cy + 2),        # lower left
        (cx - 1,  cy - s + 4),    # upper left
        (cx - 6,  cy - s + 2),    # top left
    ]


def draw_pickup(surface, pickup, ox=0, oy=0):
    """Cyan orb with DARK BLUE lightning bolt and BIG pulsing rings."""
    cx = pickup.x + pickup.SIZE // 2 + ox
    cy = pickup.y + pickup.SIZE // 2 + oy
    r = pickup.SIZE // 2
    
    # --- Pulsing outer glow rings (TWICE AS LARGE) ---
    # 4 rings, each pulsing out of phase
    for i in range(4):
        ring_offset = int(math.sin(pickup.pulse * 1.2 + i * 0.8) * 3) + i * 2
        # Vary the glow color slightly
        if i == 0:
            glow_color = (200, 230, 255)  # very light blue (outer)
        elif i == 1:
            glow_color = (150, 220, 255)  # light cyan
        elif i == 2:
            glow_color = (100, 200, 255)  # cyan-blue
        else:
            glow_color = CYAN             # cyan (innermost)
        pygame.draw.circle(surface, glow_color, (cx, cy), r + ring_offset, 2)
    
    # --- Main cyan body ---
    pygame.draw.circle(surface, CYAN, (cx, cy), r)
    
    # --- White outline ---
    pygame.draw.circle(surface, WHITE, (cx, cy), r, 2)
    
    # --- Lightning bolt (DARK BLUE, bigger) ---
    bolt = _lightning_points(cx, cy, 11)   # bigger size
    DARK_BLUE = (0, 50, 150)
    pygame.draw.polygon(surface, DARK_BLUE, bolt)
    pygame.draw.polygon(surface, WHITE, bolt, 1)   # white outline so it pops


# ============================================================
# LIFE PICKUP — gold circle with a wrench + screwdriver in an X
# (heal-kit style design)
# ============================================================

_TOOL_HANDLE_COLOR = (80, 50, 20)    # dark brown for handles/tip
_TOOL_SHAFT_COLOR  = (140, 140, 140) # mid gray for the screwdriver shaft
_TOOL_OUTLINE      = WHITE
_GOLD              = (255, 200, 0)


def _make_wrench_surface():
    """Pre-render a wrench on a transparent surface, axis along +X.
    The C-shape head (opening to the right) is at x>0; the handle is at x<0..head.
    Drawn 26x14, tool extends from x=0 to x=26 (centered at x=13)."""
    surf = pygame.Surface((26, 14), pygame.SRCALPHA)

    # Handle: x=0 to x=12, y=5 to y=9 (12 wide, 4 tall)
    pygame.draw.rect(surf, _TOOL_HANDLE_COLOR, (0, 5, 12, 4))
    pygame.draw.rect(surf, _TOOL_OUTLINE, (0, 5, 12, 4), 1)

    # Head: C-shape with the opening facing +X (to the right)
    head_points = [
        (10, 0),     # top-left of head
        (18, 0),     # top of C
        (18, 4),     # inner-top (mouth corner)
        (26, 4),     # top-right of head (outer)
        (26, 10),    # bottom-right of head (outer)
        (18, 10),    # inner-bottom (mouth corner)
        (18, 14),    # bottom of C
        (10, 14),    # bottom-left of head
    ]
    pygame.draw.polygon(surf, _TOOL_HANDLE_COLOR, head_points)
    pygame.draw.polygon(surf, _TOOL_OUTLINE, head_points, 1)

    return surf


def _make_screwdriver_surface():
    """Pre-render a screwdriver on a transparent surface, axis along +X.
    Handle is at x<0, shaft in middle, flat tip at x>0.
    Drawn 26x14, tool extends from x=0 to x=26 (centered at x=13)."""
    surf = pygame.Surface((26, 14), pygame.SRCALPHA)

    # Handle: x=0 to x=10, y=2 to y=12 (10x10, thick)
    pygame.draw.rect(surf, _TOOL_HANDLE_COLOR, (0, 2, 10, 10))
    pygame.draw.rect(surf, _TOOL_OUTLINE, (0, 2, 10, 10), 1)

    # Shaft: x=10 to x=22, y=6 to y=8 (thin)
    pygame.draw.rect(surf, _TOOL_SHAFT_COLOR, (10, 6, 12, 2))
    pygame.draw.rect(surf, _TOOL_OUTLINE, (10, 6, 12, 2), 1)

    # Tip: x=22 to x=26, y=4 to y=10 (flat, wider than shaft)
    pygame.draw.rect(surf, _TOOL_HANDLE_COLOR, (22, 4, 4, 6))
    pygame.draw.rect(surf, _TOOL_OUTLINE, (22, 4, 4, 6), 1)

    return surf


def draw_life_pickup(surface, pickup, ox=0, oy=0):
    """Gold/yellow circle with a screwdriver and wrench in an X (heal-kit design).
    Wrench head ends up at top-left, screwdriver tip at top-right,
    both handles at the bottom — symmetrical and clear."""
    cx = pickup.x + pickup.SIZE // 2 + ox
    cy = pickup.y + pickup.SIZE // 2 + oy
    r = pickup.SIZE // 2

    # --- Pulsing outer glow rings (gold tones) ---
    for i in range(4):
        ring_offset = int(math.sin(pickup.pulse * 1.2 + i * 0.8) * 3) + i * 2
        if i == 0:
            glow_color = (255, 240, 180)   # very light gold (outer)
        elif i == 1:
            glow_color = (255, 220, 120)   # light gold
        elif i == 2:
            glow_color = (255, 200, 80)    # gold
        else:
            glow_color = (255, 180, 0)     # darker gold
        pygame.draw.circle(surface, glow_color, (cx, cy), r + ring_offset, 2)

    # --- Main gold body + white outline ---
    pygame.draw.circle(surface, _GOLD, (cx, cy), r)
    pygame.draw.circle(surface, WHITE, (cx, cy), r, 2)

    # --- Wrench: rotated 135° CCW so the head is at the top-left
    #     of the X, handle at the bottom-right ---
    wrench_surf = _make_wrench_surface()
    rotated_wrench = pygame.transform.rotate(wrench_surf, 135)
    wrench_rect = rotated_wrench.get_rect(center=(cx, cy))
    surface.blit(rotated_wrench, wrench_rect)

    # --- Screwdriver: rotated 45° CCW so the flat tip is at the top-right
    #     of the X, handle at the bottom-left ---
    screw_surf = _make_screwdriver_surface()
    rotated_screw = pygame.transform.rotate(screw_surf, 45)
    screw_rect = rotated_screw.get_rect(center=(cx, cy))
    surface.blit(rotated_screw, screw_rect)