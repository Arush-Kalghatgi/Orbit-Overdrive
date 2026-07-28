import pygame

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
        try:
            s = pygame.mixer.Sound(f"sounds/{name}")
            sounds_loaded += 1
            print(f"Loaded: sounds/{name}")
            return s
        except (pygame.error, FileNotFoundError) as e:
            print(f"Could not load sounds/{name}: {e}")
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
        try:
            pygame.mixer.music.load("sounds/bgm.mp3")
            pygame.mixer.music.set_volume(music_volume)
        except (pygame.error, FileNotFoundError) as e:
            print(f"Could not load music: {e}")


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
        pygame.mixer.music.play(loops)


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