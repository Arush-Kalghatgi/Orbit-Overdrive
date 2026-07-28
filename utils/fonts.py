import pygame
import os

# Path to the fonts folder — this resolves to <project_root>/assets/
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
FONT_PATH = os.path.join(ASSETS_DIR, "PressStart2P-Regular.ttf")

_fonts = {}
_warned = False


def get_font(size):
    """Get the Press Start 2P font. Falls back to default ONLY if the file
    truly can't be found, and prints a loud warning the first time so this
    never fails silently again."""
    global _warned
    if size in _fonts:
        return _fonts[size]

    try:
        font = pygame.font.Font(FONT_PATH, size)
    except (FileNotFoundError, pygame.error) as e:
        if not _warned:
            print("=" * 60)
            print(f"[FONT ERROR] Could not load Press Start 2P from:")
            print(f"  {FONT_PATH}")
            print(f"  Reason: {e}")
            print(f"  Falling back to default pygame font for ALL text.")
            print("=" * 60)
            _warned = True
        font = pygame.font.Font(None, size)

    _fonts[size] = font
    return font


def has_custom_font():
    return os.path.exists(FONT_PATH)