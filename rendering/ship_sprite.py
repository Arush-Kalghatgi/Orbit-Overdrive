import pygame
import math
import random
import settings
from settings import WHITE, ORANGE, YELLOW
from entities import boost


# ============================================================
# PLAYER SPACESHIP — alien mech style, points upward
# Inspired by the reference: silver/white hull, dark inner panels,
# cyan accents, glowing cockpit, sharp swept-back wings,
# split nose with a small front gap.
# ============================================================
_ship_surface = None
_ship_width = 40
_ship_height = 40

LIGHT_DIR = (-0.7, -0.7)
LIGHT_ANGLE = math.atan2(LIGHT_DIR[1], LIGHT_DIR[0])


def _normalize(v):
    mag = math.hypot(v[0], v[1])
    if mag == 0:
        return (0.0, 0.0)
    return (v[0] / mag, v[1] / mag)


def _build_ship_surface():
    """Build the silver/cyan alien-fighter spaceship with a split nose.
    Sprite points UPWARD (nose at top, engines at bottom)."""

    global _ship_surface

    surf = pygame.Surface((_ship_width, _ship_height), pygame.SRCALPHA)

    # --- Color palette ---
    HULL_OUTER = (210, 220, 230)
    HULL_OUTER_LIGHT = (240, 245, 252)
    HULL_OUTER_DARK = (140, 152, 170)

    INNER_PANEL = (40, 48, 60)
    INNER_PANEL_HIGHLIGHT = (70, 82, 100)
    INNER_PANEL_DEEP = (20, 24, 32)         # for the deepest part of the front gap

    CYAN_ACCENT = (100, 230, 255)
    CYAN_BRIGHT = (180, 250, 255)
    CYAN_GLOW = (60, 200, 240)
    CYAN_DEEP = (20, 130, 200)

    WHITE_FINE = WHITE

    # ============================================================
    # SPLIT NOSE — two small tip points with a notch between them
    # ============================================================
    # Instead of a single point at (20, 2), the nose has:
    #   - left tip at (19, 2)
    #   - notch (deepest point of the gap) at (20, 5)
    #   - right tip at (21, 2)
    # The dark inner panel shows through the notch, creating the "gap"
    # effect like in the reference.

    # --- Main outer hull silhouette (with split nose) ---
    outer_hull = [
        # Left tip of the split nose
        (19, 2),
        # Upper-left spike
        (10, 8),
        (4, 18),
        (2, 22),
        (4, 24),
        # Mid-left shoulder
        (8, 26),
        # Lower-left claw
        (5, 32),
        (3, 36),
        (7, 36),
        (12, 32),
        # Lower body
        (15, 36),
        # Center bottom (where engines are)
        (17, 38),
        (23, 38),
        (25, 36),
        # Lower-right claw (mirror)
        (28, 32),
        (33, 36),
        (37, 36),
        (35, 32),
        # Mid-right shoulder
        (32, 26),
        (36, 24),
        (38, 22),
        (36, 18),
        (30, 8),
        # Right tip of the split nose
        (21, 2),
    ]
    outer_hull = [(int(x), int(y)) for x, y in outer_hull]

    # --- Drop shadow ---
    shadow_offset_x, shadow_offset_y = 2, 2
    shadow_hull = [(p[0] + shadow_offset_x, p[1] + shadow_offset_y) for p in outer_hull]
    pygame.draw.polygon(surf, (0, 0, 0, 95), shadow_hull)

    # --- Main silver hull fill ---
    pygame.draw.polygon(surf, HULL_OUTER, outer_hull)
    pygame.draw.polygon(surf, WHITE_FINE, outer_hull, 1)

    # ============================================================
    # THE FRONT GAP — dark inner panel showing through the split nose
    # ============================================================
    # A narrow dark polygon between the two tip points, going down
    # through the center of the ship. This creates the "gap on the front"
    # from the reference — the silver hull parts around it, and the
    # dark inner panel is visible.
    front_gap = [
        (19, 2),      # left tip
        (21, 2),      # right tip
        (21, 5),      # right edge going down
        (20, 6),      # narrowing
        (19, 5),      # left edge going down
    ]
    # Draw the gap as a deep dark color
    pygame.draw.polygon(surf, INNER_PANEL_DEEP, front_gap)
    pygame.draw.polygon(surf, INNER_PANEL, front_gap, 1)

    # --- The dark vertical line through the center ---
    # Like in the reference: a dark line running from the notch down
    # through the body, visible between the cyan accent lines
    pygame.draw.line(surf, INNER_PANEL_DEEP, (20, 6), (20, 33), 1)
    # Slightly wider at the top (where the notch is) to emphasize the gap
    pygame.draw.line(surf, INNER_PANEL_DEEP, (19, 7), (19, 12), 1)
    pygame.draw.line(surf, INNER_PANEL_DEEP, (21, 7), (21, 12), 1)

    # --- Dark inner panels (the "gaps" between the silver parts) ---
    upper_left_panel = [
        (20, 6),
        (12, 10),
        (8, 16),
        (11, 18),
        (16, 14),
    ]
    pygame.draw.polygon(surf, INNER_PANEL, upper_left_panel)
    pygame.draw.polygon(surf, INNER_PANEL_HIGHLIGHT, upper_left_panel, 1)

    upper_right_panel = [
        (20, 6),
        (28, 10),
        (32, 16),
        (29, 18),
        (24, 14),
    ]
    pygame.draw.polygon(surf, INNER_PANEL, upper_right_panel)
    pygame.draw.polygon(surf, INNER_PANEL_HIGHLIGHT, upper_right_panel, 1)

    lower_left_panel = [
        (10, 22),
        (7, 28),
        (10, 30),
        (14, 27),
        (14, 24),
    ]
    pygame.draw.polygon(surf, INNER_PANEL, lower_left_panel)
    pygame.draw.polygon(surf, INNER_PANEL_HIGHLIGHT, lower_left_panel, 1)

    lower_right_panel = [
        (30, 22),
        (33, 28),
        (30, 30),
        (26, 27),
        (26, 24),
    ]
    pygame.draw.polygon(surf, INNER_PANEL, lower_right_panel)
    pygame.draw.polygon(surf, INNER_PANEL_HIGHLIGHT, lower_right_panel, 1)

    # Center dark panel
    center_panel = [
        (20, 8),
        (17, 14),
        (17, 22),
        (20, 26),
        (23, 22),
        (23, 14),
    ]
    pygame.draw.polygon(surf, INNER_PANEL, center_panel)
    pygame.draw.polygon(surf, INNER_PANEL_HIGHLIGHT, center_panel, 1)

    # --- Cyan accent strips along the wing edges ---
    upper_left_strip = [
        (19, 2),
        (10, 8),
        (4, 18),
        (2, 22),
    ]
    for i in range(len(upper_left_strip) - 1):
        pygame.draw.line(surf, CYAN_ACCENT,
                         upper_left_strip[i], upper_left_strip[i + 1], 2)

    upper_right_strip = [
        (21, 2),
        (30, 8),
        (36, 18),
        (38, 22),
    ]
    for i in range(len(upper_right_strip) - 1):
        pygame.draw.line(surf, CYAN_ACCENT,
                         upper_right_strip[i], upper_right_strip[i + 1], 2)

    lower_left_strip = [
        (8, 26),
        (5, 32),
        (3, 36),
    ]
    for i in range(len(lower_left_strip) - 1):
        pygame.draw.line(surf, CYAN_ACCENT,
                         lower_left_strip[i], lower_left_strip[i + 1], 2)

    lower_right_strip = [
        (32, 26),
        (35, 32),
        (37, 36),
    ]
    for i in range(len(lower_right_strip) - 1):
        pygame.draw.line(surf, CYAN_ACCENT,
                         lower_right_strip[i], lower_right_strip[i + 1], 2)

    # --- Glowing cyan cockpit ---
    cockpit_outer = [
        (20, 11),
        (18, 13),
        (18, 16),
        (20, 18),
        (22, 16),
        (22, 13),
    ]
    glow_outer = [
        (20, 10),
        (17, 13),
        (17, 17),
        (20, 19),
        (23, 17),
        (23, 13),
    ]
    pygame.draw.polygon(surf, CYAN_GLOW, glow_outer)
    pygame.draw.polygon(surf, CYAN_ACCENT, cockpit_outer)
    pygame.draw.circle(surf, CYAN_BRIGHT, (20, 14), 1)
    pygame.draw.circle(surf, WHITE_FINE, (19, 13), 1)
    pygame.draw.polygon(surf, CYAN_DEEP, cockpit_outer, 1)

    # --- Vertical blue/cyan accent lines down the body ---
    # These flank the central dark line, like the reference's vertical stripes
    pygame.draw.line(surf, CYAN_ACCENT, (17, 20), (17, 32), 1)
    pygame.draw.line(surf, CYAN_ACCENT, (23, 20), (23, 32), 1)

    # --- Small accent details on the inner panels ---
    pygame.draw.circle(surf, CYAN_ACCENT, (12, 14), 1)
    pygame.draw.circle(surf, CYAN_ACCENT, (28, 14), 1)
    pygame.draw.circle(surf, CYAN_ACCENT, (12, 26), 1)
    pygame.draw.circle(surf, CYAN_ACCENT, (28, 26), 1)

    # --- Engine vents (at the bottom) ---
    pygame.draw.rect(surf, (15, 15, 20), (17, 35, 3, 3))
    pygame.draw.rect(surf, (15, 15, 20), (20, 35, 3, 3))
    pygame.draw.rect(surf, INNER_PANEL_HIGHLIGHT, (17, 35, 3, 3), 1)
    pygame.draw.rect(surf, INNER_PANEL_HIGHLIGHT, (20, 35, 3, 3), 1)
    pygame.draw.line(surf, (255, 140, 50), (17, 35), (19, 35), 1)
    pygame.draw.line(surf, (255, 140, 50), (20, 35), (22, 35), 1)

    # --- Top-edge highlight ---
    for p in [(19, 2), (21, 2), (10, 8), (30, 8), (4, 18), (36, 18)]:
        pygame.draw.circle(surf, HULL_OUTER_LIGHT, p, 1)

    # --- Small antenna spike at the very top ---
    pygame.draw.line(surf, HULL_OUTER_DARK, (20, 0), (20, -1), 1)
    pygame.draw.circle(surf, CYAN_ACCENT, (20, 0), 1)

    _ship_surface = surf


_build_ship_surface()


def draw_spaceship(surface, x, y, ox=0, oy=0, moving=False, time_elapsed=0.0):
    """Draw the player ship + animated engine flame."""
    is_boosting = boost.boost_active

    if is_boosting:
        flame_height = random.randint(14, 24)
        flame_width = random.randint(10, 18)
        outer_color = (100, 200, 255)
        inner_color = WHITE
    else:
        flame_height = random.randint(6, 14)
        flame_width = random.randint(8, 12)
        outer_color = ORANGE
        inner_color = YELLOW

    flame_x = x + _ship_width // 2 - flame_width // 2
    flame_y = y + _ship_height - 2

    surface.blit(_ship_surface, (x + ox, y + oy))

    # --- Running lights on the wingtips ---
    pulse = (math.sin(time_elapsed * 3) + 1) / 2
    red_intensity = int(150 + 100 * pulse)
    green_intensity = int(150 + 100 * (1 - pulse))

    pygame.draw.circle(surface, (red_intensity, 30, 30),
                       (x + 5 + ox, y + 34 + oy), 2)
    pygame.draw.circle(surface, (255, 100, 100),
                       (x + 5 + ox, y + 34 + oy), 1)

    pygame.draw.circle(surface, (30, green_intensity, 30),
                       (x + 35 + ox, y + 34 + oy), 2)
    pygame.draw.circle(surface, (100, 255, 100),
                       (x + 35 + ox, y + 34 + oy), 1)

    # --- Outer flame ---
    flame_points = [
        (flame_x + flame_width // 2, flame_y + flame_height),
        (flame_x, flame_y),
        (flame_x + flame_width, flame_y),
    ]
    pygame.draw.polygon(surface, outer_color, flame_points)

    # --- Inner flame ---
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
# ASTEROIDS (more detailed: varied silhouettes, overlapping craters,
# mid-tone shading, split-rock detail on some)
# ============================================================
_asteroid_shapes = {}


def _get_asteroid_seed(asteroid_id, radius):
    """Generate or retrieve a stable shape and detail layout for this asteroid."""
    if asteroid_id not in _asteroid_shapes:
        # Silhouette variation: some asteroids have more points for more
        # irregular shapes, and we vary the radius randomness
        rng = random.Random(asteroid_id)

        if radius >= 28:
            num_points = rng.randint(13, 16)
            silhouette_irregularity = rng.uniform(0.45, 0.55)
        elif radius >= 20:
            num_points = rng.randint(11, 13)
            silhouette_irregularity = rng.uniform(0.40, 0.50)
        else:
            num_points = rng.randint(9, 11)
            silhouette_irregularity = rng.uniform(0.35, 0.45)

        # Shape variety: about 30% of asteroids are "elongated" (their
        # silhouette is stretched in one direction), making them look like
        # rocks rather than blobs
        is_elongated = rng.random() < 0.3
        if is_elongated:
            elongation_angle = rng.uniform(0, 2 * math.pi)
            elongation_factor = rng.uniform(1.2, 1.6)
        else:
            elongation_angle = 0
            elongation_factor = 1.0

        # About 20% have a "chunk missing" — a flat-ish edge on one side
        # that suggests a piece broke off
        has_missing_chunk = rng.random() < 0.2
        if has_missing_chunk:
            chunk_angle = rng.uniform(0, 2 * math.pi)
            chunk_width = rng.uniform(0.3, 0.5)  # angular width of the chunk
        else:
            chunk_angle = 0
            chunk_width = 0

        base_points = []
        for i in range(num_points):
            base_angle = (2 * math.pi * i) / num_points
            rand = rng.uniform(0, silhouette_irregularity)
            radius_factor = 1.0 - rand

            # If this point is in the "missing chunk" zone, shrink it
            if has_missing_chunk:
                angle_diff = abs(((base_angle - chunk_angle + math.pi) % (2 * math.pi)) - math.pi)
                if angle_diff < chunk_width:
                    radius_factor *= 0.6  # pull the silhouette inward

            # If elongated, stretch in the elongation direction
            if is_elongated:
                # Compute how aligned this point is with the elongation axis
                align = math.cos(base_angle - elongation_angle)
                radius_factor *= (1.0 + (elongation_factor - 1.0) * max(0, align))

            base_points.append((base_angle, radius_factor))

        rot_speed = rng.uniform(-0.015, 0.015)

        # Craters: more variation. Some are elongated (oval), some overlap.
        craters = []
        num_craters = rng.randint(3, 7)
        for c in range(num_craters):
            crater_angle = rng.uniform(0, 2 * math.pi)
            crater_dist = rng.uniform(0.15, 0.65)
            crater_size = rng.uniform(0.08, 0.20)
            # 30% chance of an elongated crater (oval, like a glancing impact)
            is_oval = rng.random() < 0.3
            if is_oval:
                crater_aspect = rng.uniform(0.4, 0.7)  # width/height ratio
                crater_orientation = rng.uniform(0, 2 * math.pi)
            else:
                crater_aspect = 1.0
                crater_orientation = 0
            craters.append((crater_angle, crater_dist, crater_size,
                            is_oval, crater_aspect, crater_orientation))

        # Highlights
        highlights = []
        num_highlights = rng.randint(2, 4)
        for h in range(num_highlights):
            h_angle = rng.uniform(0, 2 * math.pi)
            h_dist = rng.uniform(0.2, 0.6)
            h_size = rng.uniform(0.05, 0.12)
            highlights.append((h_angle, h_dist, h_size))

        # Mineral veins
        veins = []
        if radius >= 18 and num_craters >= 2:
            num_veins = rng.randint(1, 3)
            for v in range(num_veins):
                idx1 = rng.randint(0, num_craters - 1)
                idx2 = rng.randint(0, num_craters - 1)
                if idx1 == idx2:
                    idx2 = (idx1 + 1) % num_craters
                veins.append((idx1, idx2))

        # Hot cracks (only on big rocky asteroids, ~40% chance)
        hot_cracks = []
        if radius >= 25 and rng.random() < 0.4:
            num_cracks = rng.randint(1, 2)
            for h in range(num_cracks):
                start_angle = rng.uniform(0, 2 * math.pi)
                start_dist = rng.uniform(0.2, 0.5)
                length = rng.uniform(0.2, 0.5)
                crack_angle = rng.uniform(0, 2 * math.pi)
                hot_cracks.append((start_angle, start_dist, length, crack_angle))

        # Split-rock detail: about 25% of medium+ asteroids have a visible
        # "crack" line going across part of the surface, suggesting a piece
        # has broken off. This is distinct from hot cracks — it's a cool/dark
        # line, not a glowing one.
        split_rock = None
        if radius >= 20 and rng.random() < 0.25:
            split_rock = (
                rng.uniform(0, 2 * math.pi),  # start angle
                rng.uniform(0.0, 0.4),         # start dist
                rng.uniform(0.2, 0.5),         # length factor
                rng.uniform(0, 2 * math.pi),  # direction
            )

        # Mid-tone overlay seed: each asteroid has a slightly different
        # mid-tone shading pattern, generated from its id
        mid_tone_seed = rng.random()

        _asteroid_shapes[asteroid_id] = {
            "base_points": base_points,
            "rotation": 0.0,
            "rot_speed": rot_speed,
            "craters": craters,
            "highlights": highlights,
            "veins": veins,
            "hot_cracks": hot_cracks,
            "split_rock": split_rock,
            "mid_tone_seed": mid_tone_seed,
        }
    return _asteroid_shapes[asteroid_id]


def _light_dot(point, center):
    """Return a 0..1 value where 1 = fully lit (facing the light source)."""
    dx = point[0] - center[0]
    dy = point[1] - center[1]
    if dx == 0 and dy == 0:
        return 0.5
    mag = math.hypot(dx, dy)
    return (-dx / mag) * (-LIGHT_DIR[0]) + (-dy / mag) * (-LIGHT_DIR[1])


def draw_asteroid(surface, x, y, size, color, ox=0, oy=0, asteroid_id=None):
    """Draw a detailed asteroid with varied silhouette, overlapping craters,
    mid-tone shading, mineral veins, hot cracks, split-rock detail,
    environmental rim light, and a drop shadow."""
    if asteroid_id is None:
        asteroid_id = (x, y, size)

    radius = size // 2
    center_x = x + radius + ox
    center_y = y + radius + oy

    shape = _get_asteroid_seed(asteroid_id, radius)
    shape["rotation"] += shape["rot_speed"]

    if color == settings.DARK_BROWN:
        deepest = (20, 10, 0)
        dark_color = (60, 35, 15)
        mid_color = settings.DARK_BROWN
        light_color = settings.LIGHT_BROWN
        rim_color = (220, 170, 110)
        vein_color = (180, 130, 70)
        mid_tone_color = (130, 90, 50)        # NEW: between mid and light
    elif color == settings.MEDIUM_GRAY:
        deepest = (30, 30, 30)
        dark_color = settings.DARK_GRAY
        mid_color = settings.MEDIUM_GRAY
        light_color = settings.LIGHT_GRAY
        rim_color = (220, 220, 235)
        vein_color = (200, 200, 215)
        mid_tone_color = (170, 170, 185)       # NEW
    else:
        deepest = (15, 15, 15)
        dark_color = (40, 40, 40)
        mid_color = settings.DARK_GRAY
        light_color = settings.MEDIUM_GRAY
        rim_color = (200, 200, 215)
        vein_color = (180, 180, 200)
        mid_tone_color = (90, 90, 105)         # NEW

    points = []
    for base_angle, radius_factor in shape["base_points"]:
        angle = base_angle + shape["rotation"]
        r = radius * radius_factor
        px = center_x + r * math.cos(angle)
        py = center_y + r * math.sin(angle)
        points.append((px, py))

    # --- Drop shadow ---
    shadow_offset = 3
    shadow_points = [(p[0] + shadow_offset, p[1] + shadow_offset) for p in points]
    if shadow_points:
        min_x = min(p[0] for p in shadow_points)
        min_y = min(p[1] for p in shadow_points)
        max_x = max(p[0] for p in shadow_points)
        max_y = max(p[1] for p in shadow_points)
        sw = int(max_x - min_x) + 6
        sh = int(max_y - min_y) + 6
        if sw > 0 and sh > 0:
            SHADOW_SURF = pygame.Surface((sw, sh), pygame.SRCALPHA)
            local_shadow = [(p[0] - min_x + 3, p[1] - min_y + 3) for p in shadow_points]
            pygame.draw.polygon(SHADOW_SURF, (0, 0, 0, 95), local_shadow)
            surface.blit(SHADOW_SURF, (int(min_x) - 3, int(min_y) - 3))

    # --- Main fill ---
    pygame.draw.polygon(surface, mid_color, points)

    # --- Dark inner shadow (bottom-right side, away from light) ---
    shadow_overlay_points = []
    for p in points:
        lit = _light_dot(p, (center_x, center_y))
        if lit < 0.3:
            shadow_overlay_points.append(p)
    if len(shadow_overlay_points) >= 3:
        SHADOW_INNER = pygame.Surface(
            (int(max(p[0] for p in points) - min(p[0] for p in points)) + 6,
             int(max(p[1] for p in points) - min(p[1] for p in points)) + 6),
            pygame.SRCALPHA
        )
        if SHADOW_INNER.get_width() > 0 and SHADOW_INNER.get_height() > 0:
            min_x = min(p[0] for p in points)
            min_y = min(p[1] for p in points)
            local = [(p[0] - min_x + 3, p[1] - min_y + 3) for p in points]
            pygame.draw.polygon(SHADOW_INNER, (*dark_color, 130), local)
            surface.blit(SHADOW_INNER, (int(min_x) - 3, int(min_y) - 3))

    # --- Mid-tone overlay (NEW: 5th shade, on the lit side) ---
    # This adds a brighter band on the side facing the light, giving
    # the asteroid more dimensional shading
    if shape["mid_tone_seed"] > 0.4:  # only some asteroids get this
        MID_TONE = pygame.Surface(
            (int(max(p[0] for p in points) - min(p[0] for p in points)) + 6,
             int(max(p[1] for p in points) - min(p[1] for p in points)) + 6),
            pygame.SRCALPHA
        )
        if MID_TONE.get_width() > 0 and MID_TONE.get_height() > 0:
            min_x = min(p[0] for p in points)
            min_y = min(p[1] for p in points)
            local = [(p[0] - min_x + 3, p[1] - min_y + 3) for p in points]
            pygame.draw.polygon(MID_TONE, (*mid_tone_color, 100), local)
            surface.blit(MID_TONE, (int(min_x) - 3, int(min_y) - 3))

    # --- White outline ---
    pygame.draw.polygon(surface, WHITE, points, 1)

    # --- Split-rock detail (NEW: dark crack line across part of the surface) ---
    if shape["split_rock"] is not None:
        start_angle, start_dist, length_factor, direction = shape["split_rock"]
        sa = start_angle + shape["rotation"]
        sx = center_x + radius * start_dist * math.cos(sa)
        sy = center_y + radius * start_dist * math.sin(sa)
        ex = sx + length_factor * radius * math.cos(direction)
        ey = sy + length_factor * radius * math.sin(direction)
        # Dark line (looks like a crack)
        pygame.draw.line(surface, deepest,
                         (int(sx), int(sy)), (int(ex), int(ey)), 2)
        pygame.draw.line(surface, dark_color,
                         (int(sx), int(sy)), (int(ex), int(ey)), 1)

    # --- Mineral veins ---
    if shape["veins"] and radius >= 18:
        craters = shape["craters"]
        for idx1, idx2 in shape["veins"]:
            if idx1 < len(craters) and idx2 < len(craters):
                for crater_idx in (idx1, idx2):
                    ca_angle, ca_dist, ca_size, _, _, _ = craters[crater_idx]
                    ca = ca_angle + shape["rotation"]
                    cx = center_x + radius * ca_dist * math.cos(ca)
                    cy = center_y + radius * ca_dist * math.sin(ca)
                    if crater_idx == idx1:
                        vx1, vy1 = cx, cy
                    else:
                        vx2, vy2 = cx, cy
                pygame.draw.line(
                    surface, vein_color,
                    (int(vx1), int(vy1)), (int(vx2), int(vy2)), 1
                )
                mid_x = (vx1 + vx2) / 2
                mid_y = (vy1 + vy2) / 2
                pygame.draw.circle(surface, vein_color,
                                   (int(mid_x), int(mid_y)), 1)

    # --- Hot cracks ---
    for start_angle, start_dist, length, crack_angle in shape["hot_cracks"]:
        sa = start_angle + shape["rotation"]
        sx = center_x + radius * start_dist * math.cos(sa)
        sy = center_y + radius * start_dist * math.sin(sa)
        ex = sx + length * radius * math.cos(crack_angle)
        ey = sy + length * radius * math.sin(crack_angle)
        pygame.draw.line(surface, (180, 60, 20),
                         (int(sx), int(sy)), (int(ex), int(ey)), 3)
        pygame.draw.line(surface, (255, 140, 40),
                         (int(sx), int(sy)), (int(ex), int(ey)), 1)
        brightest_x = sx + (ex - sx) * 0.3
        brightest_y = sy + (ey - sy) * 0.3
        pygame.draw.circle(surface, (255, 220, 150),
                           (int(brightest_x), int(brightest_y)), 1)

    # --- Craters (with elongated/oval support) ---
    for crater_data in shape["craters"]:
        if len(crater_data) == 6:
            crater_angle, crater_dist, crater_size, is_oval, crater_aspect, crater_orientation = crater_data
        else:
            # Backwards compatibility
            crater_angle, crater_dist, crater_size = crater_data[:3]
            is_oval, crater_aspect, crater_orientation = False, 1.0, 0

        ca = crater_angle + shape["rotation"]
        cx = center_x + radius * crater_dist * math.cos(ca)
        cy = center_y + radius * crater_dist * math.sin(ca)

        if is_oval:
            # Draw an oval (ellipse) using a surface + draw.ellipse
            crater_r = max(2, int(radius * crater_size))
            oval_w = crater_r * 2
            oval_h = max(1, int(crater_r * 2 * crater_aspect))
            crater_surf = pygame.Surface((oval_w + 2, oval_h + 2), pygame.SRCALPHA)
            pygame.draw.ellipse(crater_surf, (*dark_color, 255), (1, 1, oval_w, oval_h))
            pygame.draw.ellipse(crater_surf, (*WHITE, 255), (1, 1, oval_w, oval_h), 1)
            # Rotate by crater_orientation
            rotated = pygame.transform.rotate(crater_surf, -math.degrees(crater_orientation))
            rect = rotated.get_rect(center=(int(cx), int(cy)))
            surface.blit(rotated, rect)
        else:
            crater_r = max(1, int(radius * crater_size))
            pygame.draw.circle(surface, dark_color, (int(cx), int(cy)), crater_r)
            pygame.draw.circle(surface, WHITE, (int(cx), int(cy)), crater_r, 1)
            # Crater rim highlight (curved inner surface, lit from upper-left)
            rim_cx = cx - crater_r * 0.5
            rim_cy = cy - crater_r * 0.5
            pygame.draw.circle(surface, light_color,
                               (int(rim_cx), int(rim_cy)), max(1, crater_r // 2))

    # --- Surface highlights ---
    for h_angle, h_dist, h_size in shape["highlights"]:
        ha = h_angle + shape["rotation"]
        hx = center_x + radius * h_dist * math.cos(ha)
        hy = center_y + radius * h_dist * math.sin(ha)
        hr = max(1, int(radius * h_size))
        pygame.draw.circle(surface, light_color, (int(hx), int(hy)), hr)

    # --- Environmental rim light (upper-left, fixed) ---
    rim_points = []
    for px, py in points:
        lit = _light_dot((px, py), (center_x, center_y))
        rim_points.append((px, py, lit))
    rim_points.sort(key=lambda t: -t[2])
    top_rim = rim_points[:4]
    if len(top_rim) >= 2:
        rim_indices = sorted(
            [points.index((px, py)) for px, py, _ in top_rim]
        )
        for i in rim_indices:
            next_i = (i + 1) % len(points)
            lit_i = _light_dot(points[i], (center_x, center_y))
            lit_next = _light_dot(points[next_i], (center_x, center_y))
            if lit_i > 0.3 or lit_next > 0.3:
                pygame.draw.line(
                    surface, rim_color,
                    (int(points[i][0]), int(points[i][1])),
                    (int(points[next_i][0]), int(points[next_i][1])),
                    2,
                )
