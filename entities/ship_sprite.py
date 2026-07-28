import pygame
import math
import random
import settings
from settings import CYAN, WHITE, ORANGE, YELLOW, DARK_GRAY, DARK_BROWN, MEDIUM_GRAY, BLACK, LIGHT_GRAY, LIGHT_BROWN
from entities import boost


# ============================================================
# PLAYER SPACESHIP (highly detailed)
# ============================================================
_ship_surface = None
_ship_width = 40
_ship_height = 40


def _build_ship_surface():
    """Build a detailed retro spaceship. All drawn once onto a transparent surface."""
    global _ship_surface
    
    surf = pygame.Surface((_ship_width, _ship_height), pygame.SRCALPHA)
    
    DARK_CYAN = (0, 100, 130)
    LIGHT_CYAN = (150, 230, 255)
    
    # --- Main hull (chevron shape, larger and more defined) ---
    hull = [
        (20, 2),                # nose
        (32, 26),               # right shoulder
        (28, 28),               # right inner notch
        (24, 32),               # right engine top
        (24, 36),               # right engine bottom
        (16, 36),               # left engine bottom
        (16, 32),               # left engine top
        (12, 28),               # left inner notch
        (8, 26),                # left shoulder
    ]
    pygame.draw.polygon(surf, CYAN, hull)
    pygame.draw.polygon(surf, WHITE, hull, 1)   # outline
    
    # --- Nose tip (lighter color) ---
    nose = [(20, 2), (16, 8), (24, 8)]
    pygame.draw.polygon(surf, LIGHT_CYAN, nose)
    
    # --- Cockpit window (small darker shape in upper hull) ---
    cockpit = [(20, 10), (16, 17), (24, 17)]
    pygame.draw.polygon(surf, DARK_CYAN, cockpit)
    pygame.draw.polygon(surf, WHITE, cockpit, 1)
    # Cockpit shine
    pygame.draw.circle(surf, LIGHT_CYAN, (19, 13), 1)
    
    # --- Wing accents (thin lines on the wings) ---
    pygame.draw.line(surf, WHITE, (10, 24), (16, 30), 1)
    pygame.draw.line(surf, WHITE, (30, 24), (24, 30), 1)
    
    # --- Side fins (small triangular details) ---
    left_fin = [(8, 26), (4, 32), (10, 30)]
    right_fin = [(32, 26), (36, 32), (30, 30)]
    pygame.draw.polygon(surf, DARK_CYAN, left_fin)
    pygame.draw.polygon(surf, DARK_CYAN, right_fin)
    pygame.draw.polygon(surf, WHITE, left_fin, 1)
    pygame.draw.polygon(surf, WHITE, right_fin, 1)
    
    # --- Engine vents (two small dark rectangles) ---
    pygame.draw.rect(surf, BLACK, (17, 36, 3, 2))
    pygame.draw.rect(surf, BLACK, (20, 36, 3, 2))
    pygame.draw.rect(surf, DARK_CYAN, (17, 36, 3, 2), 1)
    pygame.draw.rect(surf, DARK_CYAN, (20, 36, 3, 2), 1)
    
    _ship_surface = surf


_build_ship_surface()


def draw_spaceship(surface, x, y, ox=0, oy=0, moving=False):
    """Draw the player ship + animated engine flame."""
    surface.blit(_ship_surface, (x + ox, y + oy))
    
    is_boosting = boost.boost_active
    
    if is_boosting:
        flame_height = random.randint(14, 24)
        flame_width = random.randint(14, 22)
        outer_color = (100, 200, 255)   # light blue
        inner_color = WHITE
    else:
        flame_height = random.randint(6, 14)
        flame_width = random.randint(10, 16)
        outer_color = ORANGE
        inner_color = YELLOW
    
    flame_x = x + _ship_width // 2 - flame_width // 2
    flame_y = y + _ship_height - 2
    
    # Outer flame
    flame_points = [
        (flame_x + flame_width // 2, flame_y + flame_height),
        (flame_x, flame_y),
        (flame_x + flame_width, flame_y),
    ]
    pygame.draw.polygon(surface, outer_color, flame_points)
    
    # Inner flame
    inner_height = max(2, flame_height // 2)
    inner_width = max(2, flame_width // 2)
    inner_x = x + _ship_width // 2 - inner_width // 2
    inner_points = [
        (inner_x + inner_width // 2, flame_y + inner_height),
        (inner_x, flame_y),
        (inner_x + inner_width, flame_y),
    ]
    pygame.draw.polygon(surface, inner_color, inner_points)


# ============================================================
# ASTEROIDS (detailed with craters + highlights)
# ============================================================
_asteroid_shapes = {}


def _get_asteroid_seed(asteroid_id, radius):
    """Generate or retrieve a stable shape for this asteroid."""
    if asteroid_id not in _asteroid_shapes:
        num_points = 12 if radius >= 25 else 10 if radius >= 18 else 8
        base_points = []
        for i in range(num_points):
            base_angle = (2 * math.pi * i) / num_points
            rand = random.Random(asteroid_id * 1000 + i).uniform(0, 0.45)
            base_points.append((base_angle, 1.0 - rand))
        rot_speed = random.Random(asteroid_id).uniform(-0.015, 0.015)
        
        # Generate stable crater positions
        craters = []
        num_craters = random.Random(asteroid_id + 99).randint(2, 5)
        for c in range(num_craters):
            crater_angle = random.Random(asteroid_id + 200 + c).uniform(0, 2 * math.pi)
            crater_dist = random.Random(asteroid_id + 300 + c).uniform(0.2, 0.55)
            crater_size = random.Random(asteroid_id + 400 + c).uniform(0.08, 0.18)
            craters.append((crater_angle, crater_dist, crater_size))
        
        _asteroid_shapes[asteroid_id] = {
            "base_points": base_points,
            "rotation": 0.0,
            "rot_speed": rot_speed,
            "craters": craters,
        }
    return _asteroid_shapes[asteroid_id]


def draw_asteroid(surface, x, y, size, color, ox=0, oy=0, asteroid_id=None):
    """Draw a detailed asteroid with craters and surface highlights."""
    if asteroid_id is None:
        asteroid_id = (x, y, size)
    
    radius = size // 2
    center_x = x + radius + ox
    center_y = y + radius + oy
    
    shape = _get_asteroid_seed(asteroid_id, radius)
    shape["rotation"] += shape["rot_speed"]
    
    # Determine darker / lighter shades of the base color
    if color == DARK_BROWN:
        dark_color = (60, 40, 20)
        light_color = LIGHT_BROWN
    elif color == MEDIUM_GRAY:
        dark_color = DARK_GRAY
        light_color = LIGHT_GRAY
    else:  # DARK_GRAY
        dark_color = (40, 40, 40)
        light_color = MEDIUM_GRAY
    
    # --- Build the current outline points ---
    points = []
    for base_angle, radius_factor in shape["base_points"]:
        angle = base_angle + shape["rotation"]
        r = radius * radius_factor
        px = center_x + r * math.cos(angle)
        py = center_y + r * math.sin(angle)
        points.append((px, py))
    
    # Fill
    pygame.draw.polygon(surface, color, points)
    # White outline
    pygame.draw.polygon(surface, WHITE, points, 1)
    
    # --- Draw craters (darker spots) ---
    for crater_angle, crater_dist, crater_size in shape["craters"]:
        # Crater position rotates with the asteroid
        ca = crater_angle + shape["rotation"]
        cx = center_x + radius * crater_dist * math.cos(ca)
        cy = center_y + radius * crater_dist * math.sin(ca)
        crater_r = max(1, int(radius * crater_size))
        pygame.draw.circle(surface, dark_color, (int(cx), int(cy)), crater_r)
        pygame.draw.circle(surface, WHITE, (int(cx), int(cy)), crater_r, 1)
    
    # --- Add a few surface highlights (lighter spots) ---
    # Use asteroid_id + fixed offset for stable highlights
    highlight_seed = random.Random(asteroid_id + 555)
    for _ in range(2):
        h_angle = highlight_seed.uniform(0, 2 * math.pi) + shape["rotation"]
        h_dist = highlight_seed.uniform(0.3, 0.6)
        h_size = highlight_seed.uniform(0.05, 0.1)
        hx = center_x + radius * h_dist * math.cos(h_angle)
        hy = center_y + radius * h_dist * math.sin(h_angle)
        hr = max(1, int(radius * h_size))
        pygame.draw.circle(surface, light_color, (int(hx), int(hy)), hr)