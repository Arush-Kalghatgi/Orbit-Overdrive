import pygame
import random
import settings
from settings import YELLOW, ORANGE, RED, CYAN, WHITE, DARK_GRAY, GREEN, GRAY
from utils.fonts import get_font
from utils import sound


# --- Boost State ---
boost_active = False
boost_fuel = 10.0
MAX_FUEL = 10.0
BOOST_DRAIN = 1.0
PASSIVE_SCORE_MULTIPLIER = 4.0
KILL_SCORE_MULTIPLIER = 2.0
WORLD_FAST_FACTOR = 3.0

BOOST_SHAKE_INTENSITY = 3
BOOST_SHAKE_INTERVAL = 3
_frame_counter = 0
_boost_shake_x = 0
_boost_shake_y = 0

_prev_active = False
_boost_channel = None

# --- Boost Sound Loop ---
# The boost sound file is ~6 seconds long but the boost itself lasts 10 seconds.
# We restart the sound at 5.5s so the full boost has continuous audio with no gap.
_boost_sound_time = 0.0
BOOST_SOUND_LOOP_TIME = 5.5


def update(dt):
    global boost_fuel, boost_active, _frame_counter
    global _boost_shake_x, _boost_shake_y, _boost_sound_time, _boost_channel

    if boost_active and boost_fuel > 0:
        boost_fuel -= BOOST_DRAIN * dt
        if boost_fuel <= 0:
            boost_fuel = 0
            boost_active = False

        # Track how long the boost sound has been playing; restart it
        # before it ends so the 10s boost doesn't have a 4s audio gap.
        _boost_sound_time += dt
        if _boost_sound_time >= BOOST_SOUND_LOOP_TIME:
            if _boost_channel is not None:
                _boost_channel.stop()
            _boost_channel = sound.play_on_channel(sound.BOOST_SOUND)
            _boost_sound_time = 0.0
    else:
        _boost_sound_time = 0.0

    _frame_counter += 1
    if boost_active and _frame_counter % BOOST_SHAKE_INTERVAL == 0:
        _boost_shake_x = random.randint(-BOOST_SHAKE_INTENSITY, BOOST_SHAKE_INTENSITY)
        _boost_shake_y = random.randint(-BOOST_SHAKE_INTENSITY, BOOST_SHAKE_INTENSITY)
    elif not boost_active:
        _boost_shake_x = int(_boost_shake_x * 0.7)
        _boost_shake_y = int(_boost_shake_y * 0.7)


def add_fuel(amount):
    global boost_fuel
    old = boost_fuel
    boost_fuel = min(MAX_FUEL, boost_fuel + amount)
    return boost_fuel - old


def check_transition():
    global _prev_active, _boost_channel, _boost_sound_time

    just_activated = boost_active and not _prev_active
    just_deactivated = (not boost_active) and _prev_active

    if just_activated:
        _prev_active = True
        _boost_sound_time = 0.0
        return "activated", None
    elif just_deactivated:
        _prev_active = False
        if _boost_channel is not None:
            _boost_channel.stop()
            _boost_channel = None
        return "deactivated", None
    else:
        _prev_active = boost_active
        return None, None


def set_boost_channel(channel):
    global _boost_channel
    _boost_channel = channel


def stop_boost_sound():
    global _boost_channel, _boost_sound_time
    if _boost_channel is not None:
        _boost_channel.stop()
        _boost_channel = None
    _boost_sound_time = 0.0


def get_boost_shake_offset():
    if boost_active:
        return _boost_shake_x, _boost_shake_y
    return 0, 0


def get_world_fast_factor():
    return WORLD_FAST_FACTOR if boost_active else 1.0


def get_passive_score_multiplier():
    return PASSIVE_SCORE_MULTIPLIER if boost_active else 1.0


def get_kill_score_multiplier():
    return KILL_SCORE_MULTIPLIER if boost_active else 1.0


def draw_fuel_bar(surface, x, y):
    label = get_font(20).render("TURBO", True, WHITE)
    surface.blit(label, (x, y))

    bar_x = x
    bar_y = y + 30
    bar_width = 230
    bar_height = 18

    pygame.draw.rect(surface, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))

    fill_ratio = boost_fuel / MAX_FUEL if MAX_FUEL > 0 else 0
    fill_width = int(bar_width * fill_ratio)

    if fill_ratio > 0.5:
        color = CYAN
    elif fill_ratio > 0.25:
        color = YELLOW
    else:
        color = RED

    pygame.draw.rect(surface, color, (bar_x, bar_y, fill_width, bar_height))
    pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

    if boost_active:
        active_text = get_font(16).render(">> ACTIVE <<", True, CYAN)
        surface.blit(active_text, (bar_x + bar_width + 10, bar_y - 1))