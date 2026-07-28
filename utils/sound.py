import pygame
import os
import sys

# Path to the sounds folder — this resolves to <project_root>/sounds/
# when run normally with `python main.py`.
#
# Same story as fonts.py: when packaged with PyInstaller (--onefile),
# relative strings like "sounds/shoot.wav" only work if the current
# working directory happens to match where the files were extracted to,
# which isn't reliable. So we detect the frozen case and build an
# absolute path instead.
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    # Running as a PyInstaller-built exe.
    BASE_DIR = sys._MEIPASS
else:
    # Running normally via `python main.py`.
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")

# Module-level state
SOUND_ENABLED = False
SHOOT_SOUND = None
EXPLOSION_SOUND = None
HIT_SOUND = None
GAMEOVER_SOUND = None
BOOST_SOUND = None
PICKUP_SOUND = None      # NEW

music_volume = 0.4
sfx_volume = 0.4


def initialize():
    global SOUND_ENABLED, SHOOT_SOUND, EXPLOSION_SOUND, HIT_SOUND, GAMEOVER_SOUND
    global BOOST_SOUND, PICKUP_SOUND

    sounds_loaded = 0

    def _try_load(name):
        nonlocal sounds_loaded
        path = os.path.join(SOUNDS_DIR, name)
        try:
            s = pygame.mixer.Sound(path)
            sounds_loaded += 1
            print(f"Loaded: {path}")
            return s
        except (pygame.error, FileNotFoundError) as e:
            print(f"Could not load {path}: {e}")
            return None

    SHOOT_SOUND     = _try_load("shoot.wav")
    EXPLOSION_SOUND = _try_load("explosion.wav")
    HIT_SOUND       = _try_load("hit.wav")
    GAMEOVER_SOUND  = _try_load("gameover.wav")
    BOOST_SOUND     = _try_load("boost.wav")
    PICKUP_SOUND    = _try_load("powerup.wav")    # NEW

    SOUND_ENABLED = sounds_loaded > 0

    if SOUND_ENABLED:
        apply_volumes()
        music_path = os.path.join(SOUNDS_DIR, "bgm.mp3")
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(music_volume)
        except (pygame.error, FileNotFoundError) as e:
            print(f"Could not load music from {music_path}: {e}")


def apply_volumes():
    def _safe_set(sound, vol):
        if sound is not None:
            sound.set_volume(vol)

    _safe_set(SHOOT_SOUND, sfx_volume)
    _safe_set(EXPLOSION_SOUND, sfx_volume)
    _safe_set(HIT_SOUND, sfx_volume)
    _safe_set(GAMEOVER_SOUND, sfx_volume)
    _safe_set(BOOST_SOUND, sfx_volume)
    _safe_set(PICKUP_SOUND, sfx_volume)     # NEW

    try:
        pygame.mixer.music.set_volume(music_volume)
    except pygame.error:
        pass


def play(sound):
    if SOUND_ENABLED and sound is not None:
        sound.play()


def play_on_channel(sound):
    """Play sound and return the channel (so it can be stopped later)."""
    if SOUND_ENABLED and sound is not None:
        return sound.play()
    return None


def play_music(loops=-1):
    if SOUND_ENABLED:
        try:
            pygame.mixer.music.play(loops)
        except pygame.error as e:
            print(f"Could not play music: {e}")


def stop_music():
    pygame.mixer.music.stop()


def toggle_enabled():
    global SOUND_ENABLED
    SOUND_ENABLED = not SOUND_ENABLED
    if SOUND_ENABLED:
        apply_volumes()
        play_music()
    else:
        stop_music()
    return SOUND_ENABLED


def set_music_volume(value):
    global music_volume
    music_volume = max(0.0, min(1.0, value))
    apply_volumes()


def set_sfx_volume(value):
    global sfx_volume
    sfx_volume = max(0.0, min(1.0, value))
    apply_volumes()