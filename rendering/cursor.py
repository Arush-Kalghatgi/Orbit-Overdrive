import pygame

# 16x16 retro crosshair cursor, scaled up 2x for visibility.
# Drawn once and cached. Hot-pink center, white outline, fully pixel.
_CURSOR_SIZE = 16
_SCALE = 2  # bump this to make the cursor bigger/smaller
_DISPLAY_SIZE = _CURSOR_SIZE * _SCALE
_cursor_surface = None
_CURSOR_HOTSPOT = (_DISPLAY_SIZE // 2, _DISPLAY_SIZE // 2)  # center of the scaled sprite

# 16x16 bitmap: 1 = pink center pixel, 2 = white outline,
# 0 = transparent. Designed for a "tech / target lock" feel.
_BITMAP = [
    "0000002200000000",
    "0000002200000000",
    "0000002200000000",
    "0000002200000000",
    "0000021122000000",
    "0000002112000000",
    "0000000212000000",
    "2222222221222222",
    "2222222221222222",
    "0000000212000000",
    "0000002112000000",
    "0000021122000000",
    "0000002200000000",
    "0000002200000000",
    "0000002200000000",
    "0000002200000000",
]

# Colors
_PINK = (255, 80, 180)   # hot pink center
_WHITE = (255, 255, 255)
_TRANSPARENT = (0, 0, 0, 0)


def _build():
    global _cursor_surface
    base = pygame.Surface((_CURSOR_SIZE, _CURSOR_SIZE), pygame.SRCALPHA)
    for y, row in enumerate(_BITMAP):
        for x, ch in enumerate(row):
            if ch == "1":
                base.set_at((x, y), _PINK)
            elif ch == "2":
                base.set_at((x, y), _WHITE)
            # "0" stays transparent
    # Scale up with regular (non-smooth) scale so pixels stay crisp/blocky.
    _cursor_surface = pygame.transform.scale(base, (_DISPLAY_SIZE, _DISPLAY_SIZE))


_build()


def get_cursor_surface():
    """Return the cached retro crosshair surface (and the hotspot)."""
    return _cursor_surface, _CURSOR_HOTSPOT


def draw_cursor(surface, mouse_pos):
    """Draw the retro cursor at the given screen position (uses hotspot)."""
    cx, cy = mouse_pos
    hx, hy = _CURSOR_HOTSPOT
    surface.blit(_cursor_surface, (cx - hx, cy - hy))


def show_system_cursor():
    pygame.mouse.set_visible(True)
    # Clear any custom cursor by resetting visibility; pygame will use default.


def hide_system_cursor_and_use_custom():
    pygame.mouse.set_visible(False)