import math
import pygame
import settings
from settings import YELLOW, WHITE, GRAY, GREEN, RED, BLACK, DARK_GRAY
from utils import sound
from utils.fonts import get_font
from utils.helpers import point_in_rect, value_from_slider_x


# Sliders store their drag state in this module so the event loop in main.py
# can read/write to it.
class _SliderDragState:
    active = None  # name of slider being dragged ("music" or "sfx"), or None


_drag = _SliderDragState()


def is_dragging():
    return _drag.active is not None


def get_drag_target():
    return _drag.active


def end_drag():
    _drag.active = None


def _draw_volume_row(surface, cx, top_y, label, value, slider_name):
    """Draws one centered volume row: label, bar, percent, hint.
    If the mouse is pressed inside the bar, this slider becomes the active
    drag target and the bar is filled to the mouse x position."""
    label_font = get_font(20)
    label_surf = label_font.render(label, True, WHITE)
    surface.blit(label_surf, (cx - label_surf.get_width() // 2, top_y))

    bar_width = 240
    bar_height = 22
    bar_x = cx - bar_width // 2
    bar_y = top_y + 36
    bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)

    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()[0]  # left button held

    # Update drag value if this slider is active
    if _drag.active == slider_name and mouse_pressed:
        new_val = value_from_slider_x(mouse_pos[0], bar_x, bar_width)
        if slider_name == "music":
            sound.set_music_volume(new_val)
        else:
            sound.set_sfx_volume(new_val)
        value = new_val

    # Bar background
    pygame.draw.rect(surface, DARK_GRAY, bar_rect)

    # Bar fill (use the live value, not the function arg)
    live_val = sound.music_volume if slider_name == "music" else sound.sfx_volume
    fill_width = int(bar_width * live_val)
    pygame.draw.rect(surface, GREEN, (bar_x, bar_y, fill_width, bar_height))

    # Hover/drag border
    if point_in_rect(mouse_pos[0], mouse_pos[1], bar_rect) or _drag.active == slider_name:
        border_color = YELLOW if _drag.active == slider_name else WHITE
        pygame.draw.rect(surface, border_color, bar_rect, 2)
    else:
        pygame.draw.rect(surface, WHITE, bar_rect, 1)

    percent_font = get_font(18)
    percent_text = percent_font.render(f"{int(live_val * 100)}%", True, WHITE)
    surface.blit(percent_text, (cx - percent_text.get_width() // 2, bar_y + bar_height + 10))

    hint_font = get_font(14)
    hint = hint_font.render("< LEFT / RIGHT >  OR  DRAG", True, GRAY)
    surface.blit(hint, (cx - hint.get_width() // 2, bar_y + bar_height + 36))

    return bar_rect


def get_music_slider_rect(cx, top_y):
    """Pre-compute the music slider rect for hit testing."""
    bar_width = 240
    bar_y = top_y + 36
    bar_height = 22
    bar_x = cx - bar_width // 2
    return pygame.Rect(bar_x, bar_y, bar_width, bar_height)


def get_sfx_slider_rect(cx, top_y):
    """Pre-compute the SFX slider rect for hit testing."""
    return get_music_slider_rect(cx, top_y)  # same dimensions


def draw_settings_menu(surface, time_elapsed=0.0):
    overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT))
    overlay.set_alpha(200)
    overlay.fill(BLACK)
    surface.blit(overlay, (0, 0))

    cx = settings.WIDTH // 2

    # --- Title ---
    title_font = get_font(48)
    title_shadow = title_font.render("SETTINGS", True, (100, 85, 0))
    title_main = title_font.render("SETTINGS", True, YELLOW)
    surface.blit(title_shadow, (cx - title_shadow.get_width() // 2 + 3, 53))
    surface.blit(title_main, (cx - title_main.get_width() // 2, 50))

    # --- Volume rows ---
    music_rect = _draw_volume_row(surface, cx, 170, "MUSIC VOLUME", sound.music_volume, "music")
    sfx_rect   = _draw_volume_row(surface, cx, 340, "SFX VOLUME",   sound.sfx_volume,   "sfx")

    # --- Sound toggle button ---
    toggle_font = get_font(26)
    hint_font = get_font(16)
    mouse_pos = pygame.mouse.get_pos()

    mute_status = "ON" if sound.SOUND_ENABLED else "OFF"
    mute_color = GREEN if sound.SOUND_ENABLED else RED
    sound_text = toggle_font.render(f"SOUND: {mute_status}", True, mute_color)
    sound_rect = sound_text.get_rect(center=(cx, 480 + toggle_font.get_height() // 2))
    pad = 20
    sound_btn = pygame.Rect(0, 0, sound_rect.width + pad * 2, sound_rect.height + 12)
    sound_btn.center = sound_rect.center
    if point_in_rect(mouse_pos[0], mouse_pos[1], sound_btn):
        pygame.draw.rect(surface, (50, 50, 50), sound_btn, border_radius=3)
        pygame.draw.rect(surface, WHITE, sound_btn, 2, border_radius=3)
    surface.blit(sound_text, sound_rect)

    hint1 = hint_font.render("PRESS M OR CLICK TO TOGGLE", True, GRAY)
    surface.blit(hint1, (cx - hint1.get_width() // 2, sound_btn.bottom + 8))

    # --- Fullscreen toggle button ---
    fs_color = GREEN if settings.is_fullscreen else RED
    fs_status = "ON" if settings.is_fullscreen else "OFF"
    fs_text = toggle_font.render(f"FULLSCREEN: {fs_status}", True, fs_color)
    fs_rect = fs_text.get_rect(center=(cx, 565 + toggle_font.get_height() // 2))
    fs_btn = pygame.Rect(0, 0, fs_rect.width + pad * 2, fs_rect.height + 12)
    fs_btn.center = fs_rect.center
    if point_in_rect(mouse_pos[0], mouse_pos[1], fs_btn):
        pygame.draw.rect(surface, (50, 50, 50), fs_btn, border_radius=3)
        pygame.draw.rect(surface, WHITE, fs_btn, 2, border_radius=3)
    surface.blit(fs_text, fs_rect)

    hint2 = hint_font.render("PRESS F11 OR CLICK TO TOGGLE", True, GRAY)
    surface.blit(hint2, (cx - hint2.get_width() // 2, fs_btn.bottom + 8))

    # --- Resume prompt ---
    blink = math.sin(time_elapsed * 3) > 0
    if blink:
        resume_font = get_font(20)
        resume_text = resume_font.render("PRESS ESC OR CLICK OUTSIDE TO RESUME", True, WHITE)
        surface.blit(resume_text, (cx - resume_text.get_width() // 2, settings.HEIGHT - 55))

    return {
        "music_slider": music_rect,
        "sfx_slider": sfx_rect,
        "sound_toggle": sound_btn,
        "fullscreen_toggle": fs_btn,
    }


def handle_pause_click(mx, my, rects):
    """Given a click position and the rects returned by draw_settings_menu,
    dispatch the appropriate action. Returns True if the click was consumed."""
    if point_in_rect(mx, my, rects["music_slider"]):
        _drag.active = "music"
        val = value_from_slider_x(mx, rects["music_slider"].x, rects["music_slider"].width)
        sound.set_music_volume(val)
        return True
    if point_in_rect(mx, my, rects["sfx_slider"]):
        _drag.active = "sfx"
        val = value_from_slider_x(mx, rects["sfx_slider"].x, rects["sfx_slider"].width)
        sound.set_sfx_volume(val)
        return True
    if point_in_rect(mx, my, rects["sound_toggle"]):
        sound.toggle_enabled()
        return True
    if point_in_rect(mx, my, rects["fullscreen_toggle"]):
        # Imported here to avoid circular import at module load time.
        import main as _main
        _main.toggle_fullscreen()
        return True
    return False