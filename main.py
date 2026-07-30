import sys
import random
import math
import asyncio
import pygame

pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()

import settings

from settings import (
    MONITOR_WIDTH, MONITOR_HEIGHT, MONITOR_ASPECT, WINDOW_SCALE,
    is_fullscreen, calculate_resolution, get_scale_factor, apply_display_mode,
    FPS,
    WHITE, RED, ORANGE, YELLOW, CYAN, PURPLE, GREEN, BLACK, GRAY, DARK_GRAY,
    LIGHT_BLUE, DARK_BLUE,
)
from core import sound
from utils.highscore import load_high_score, save_high_score, save_last_score
from utils.helpers import (
    create_starfield, update_and_draw_stars,
    trigger_hit_feedback, update_hit_feedback, get_slowmo_factor,
    update_constant_shake, point_in_rect,
)
from utils.fonts import get_font
from rendering import cursor as game_cursor
from rendering import menu as settings_menu
from rendering import particles as game_particles
from rendering.title import draw_title_screen, get_title_start_rect
from rendering import touch_ui
from input import manager as input_manager
from entities.player import Player
from entities.bullet import Lazer
from entities.enemy import Enemy, spawn_enemy
from entities.powerup import TurboPickup, draw_pickup, LifePickup, draw_life_pickup
from entities import boost
from rendering.ship_sprite import draw_spaceship, draw_asteroid
from rendering.hud import draw_hud, draw_game_over


# --- Display Setup ---
settings.WIDTH, settings.HEIGHT = calculate_resolution(is_fullscreen)
settings.SCALE_FACTOR = get_scale_factor(settings.HEIGHT)

screen = apply_display_mode(is_fullscreen, settings.WIDTH, settings.HEIGHT)
pygame.display.set_caption("ORBIT OVERDRIVE")

print(f"Monitor: {MONITOR_WIDTH}x{MONITOR_HEIGHT} (aspect: {MONITOR_ASPECT:.2f})")
print(f"Game: {settings.WIDTH}x{settings.HEIGHT} (scale: {settings.SCALE_FACTOR:.2f}x)")


# --- Audio Setup ---
sound.initialize()


# --- Particle Manager ---
particles = game_particles.ParticleManager()


# --- Star Field (single layer, original behavior) ---
def update_stars_with_dt(stars, dt, offset_x, offset_y):
    for star in stars:
        star[1] += star[2] * dt * 60
        if star[1] > settings.HEIGHT:
            star[1] = 0
            star[0] = random.randint(0, settings.WIDTH)
        brightness = int(100 + star[2] * 50)
        if brightness < 0:
            brightness = 0
        elif brightness > 255:
            brightness = 255
        color = (brightness, brightness, brightness)
        pygame.draw.circle(screen, color,
                           (int(star[0] + offset_x), int(star[1] + offset_y)), 1)


# --- Resolution Helper ---
def toggle_fullscreen():
    global screen, stars
    settings.is_fullscreen = not settings.is_fullscreen
    settings.WIDTH, settings.HEIGHT = calculate_resolution(settings.is_fullscreen)
    settings.SCALE_FACTOR = get_scale_factor(settings.HEIGHT)
    screen = apply_display_mode(settings.is_fullscreen, settings.WIDTH, settings.HEIGHT)
    print(f"Switched to {'fullscreen' if settings.is_fullscreen else 'windowed'}: "
          f"{settings.WIDTH}x{settings.HEIGHT}")


# --- Game Reset ---
def reset_game():
    global pickup, pickup_timer, lives_pickup
    global turbo_drops_counter, lives_drop_threshold, lives_drop_timer
    player_speed = int(6 * settings.SCALE_FACTOR)
    boost.boost_fuel = boost.MAX_FUEL
    boost.boost_active = False
    boost._prev_active = False
    boost.stop_boost_sound()
    pickup = None
    pickup_timer = random.uniform(7.0, 10.0)
    lives_pickup = None
    lives_drop_timer = 0.0
    turbo_drops_counter = 0
    lives_drop_threshold = random.randint(2, 3)
    particles.clear()
    return (
        Player(player_speed),
        [], [], 0.0, 0.0,
        random.uniform(0.5, 1.4),
        create_starfield(),
    )


# --- Hit Detection ---
def handle_collisions(player, enemies, lazers):
    enemies_to_remove = []
    lazers_to_remove = []
    score_gained = 0.0
    player_died = False
    for enemy in enemies:
        for lazer in lazers:
            if enemy.colliderect(lazer):
                impact_x = lazer.x + lazer.width // 2
                impact_y = lazer.y
                if enemy.take_damage():
                    enemies_to_remove.append(enemy)
                    if enemy.color == settings.DARK_BROWN:
                        score_gained += 10
                    elif enemy.color == settings.MEDIUM_GRAY:
                        score_gained += 20
                    else:
                        score_gained += 30
                    sound.play(sound.EXPLOSION_SOUND)
                    game_particles.spawn_explosion(
                        particles, impact_x, impact_y, enemy.color,
                        count=20, speed_range=(60, 240), size_range=(2, 5),
                        life_range=(0.4, 0.9)
                    )
                else:
                    game_particles.spawn_sparks(
                        particles, impact_x, impact_y, count=6
                    )
                lazers_to_remove.append(lazer)
    for enemy in enemies:
        if player.colliderect(enemy):
            enemies_to_remove.append(enemy)
            player.lives -= 1
            sound.play(sound.HIT_SOUND)
            trigger_hit_feedback()
            game_particles.spawn_player_hit(
                particles, player.x + player.width // 2, player.y + player.height // 2
            )
            game_particles.spawn_explosion(
                particles, enemy.x + enemy.width // 2, enemy.y + enemy.height // 2,
                enemy.color, count=14, speed_range=(50, 200), size_range=(2, 4),
                life_range=(0.3, 0.7)
            )
            if player.lives <= 0:
                player_died = True
            break
    return enemies_to_remove, lazers_to_remove, player_died, score_gained


# --- Main Loop ---
async def main():
    global player, enemies, lazers, score, spawn_timer, spawn_interval, stars, state
    global pickup, pickup_timer, lives_pickup
    global turbo_drops_counter, lives_drop_threshold, lives_drop_timer
    global pre_pause_state
    global force_touch_ui

    clock = pygame.time.Clock()
    high_score = load_high_score()
    state = "title"
    pre_pause_state = None
    selected_setting = 0
    is_new_high_score = False
    time_elapsed = 0.0
    title_stars = create_starfield()

    turbo_drops_counter = 0
    lives_drop_threshold = random.randint(2, 3)
    lives_drop_timer = 0.0

    gameover_rects = None
    pause_rects = None

    sound.play_music()

    game_cursor.hide_system_cursor_and_use_custom()

    # --- Touch / mouse input (desktop: touch UI off by default; F10 to toggle) ---
    touch_input = input_manager.InputManager()
    force_touch_ui = settings.FORCE_TOUCH_UI

    while True:
        raw_dt = clock.get_time() / 1000
        base_dt = raw_dt * get_slowmo_factor()
        dt_world = base_dt * boost.get_world_fast_factor()
        dt_real = base_dt
        time_elapsed += raw_dt

        # Tiny yield so the asyncio scheduler doesn't complain; harmless on desktop.
        await asyncio.sleep(0)

        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        left_held = mouse_pressed[0]
        right_held = mouse_pressed[2]

        if not left_held and settings_menu.is_dragging():
            settings_menu.end_drag()

        all_events = pygame.event.get()
        if force_touch_ui:
            touch_input.handle_events(all_events)

        for event in all_events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if state == "title" and event.key == pygame.K_SPACE:
                    player, enemies, lazers, score, spawn_timer, spawn_interval, stars = reset_game()
                    state = "playing"
                    sound.play_music()

                elif state == "gameover":
                    if event.key == pygame.K_SPACE:
                        player, enemies, lazers, score, spawn_timer, spawn_interval, stars = reset_game()
                        state = "playing"
                        sound.play_music()
                        is_new_high_score = False
                    elif event.key == pygame.K_m:
                        state = "title"
                        is_new_high_score = False
                        sound.play_music()

                elif event.key == pygame.K_ESCAPE:
                    if state in ("playing", "title"):
                        pre_pause_state = state
                        state = "paused"
                        settings_menu.end_drag()
                    elif state == "paused":
                        state = pre_pause_state or "playing"

                elif event.key == pygame.K_F11:
                    if state in ("paused", "gameover", "title"):
                        toggle_fullscreen()

                elif event.key == pygame.K_F10:
                    force_touch_ui = not force_touch_ui
                    settings.FORCE_TOUCH_UI = force_touch_ui

                if state == "paused":
                    if event.key == pygame.K_m:
                        sound.toggle_enabled()
                    elif event.key == pygame.K_UP:
                        selected_setting = (selected_setting - 1) % 4
                    elif event.key == pygame.K_DOWN:
                        selected_setting = (selected_setting + 1) % 4
                    elif event.key == pygame.K_LEFT:
                        if selected_setting == 0:
                            sound.set_music_volume(sound.music_volume - 0.1)
                        elif selected_setting == 1:
                            sound.set_sfx_volume(sound.sfx_volume - 0.1)
                    elif event.key == pygame.K_RIGHT:
                        if selected_setting == 0:
                            sound.set_music_volume(sound.music_volume + 0.1)
                        elif selected_setting == 1:
                            sound.set_sfx_volume(sound.sfx_volume + 0.1)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if state == "title":
                        start_rect = get_title_start_rect()
                        if point_in_rect(mouse_pos[0], mouse_pos[1], start_rect):
                            player, enemies, lazers, score, spawn_timer, spawn_interval, stars = reset_game()
                            state = "playing"
                            sound.play_music()
                    elif state == "gameover" and gameover_rects is not None:
                        if point_in_rect(mouse_pos[0], mouse_pos[1], gameover_rects["retry"]):
                            player, enemies, lazers, score, spawn_timer, spawn_interval, stars = reset_game()
                            state = "playing"
                            sound.play_music()
                            is_new_high_score = False
                        elif point_in_rect(mouse_pos[0], mouse_pos[1], gameover_rects["menu"]):
                            state = "title"
                            is_new_high_score = False
                            sound.play_music()
                    elif state == "paused" and pause_rects is not None:
                        if not settings_menu.handle_pause_click(mouse_pos[0], mouse_pos[1], pause_rects):
                            state = pre_pause_state or "playing"

        is_moving = False
        if state == "playing":
            boost.update(dt_real)
            keys = pygame.key.get_pressed()
            dx = dy = 0

            shift_held = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
            if (shift_held or right_held) and boost.boost_fuel > 0:
                boost.boost_active = True
            else:
                boost.boost_active = False

            transition, _ = boost.check_transition()
            if transition == "activated":
                channel = sound.play_on_channel(sound.BOOST_SOUND)
                boost.set_boost_channel(channel)

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx -= 1
                is_moving = True
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx += 1
                is_moving = True
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy -= 1
                is_moving = True
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy += 1
                is_moving = True

            if force_touch_ui:
                mdx, mdy = touch_input.get_movement()
                if mdx != 0.0 or mdy != 0.0:
                    dx = mdx
                    dy = mdy
                    is_moving = True
                if touch_input.is_shooting():
                    new_lazer = player.shoot()
                    if new_lazer:
                        lazers.append(new_lazer)
                        sound.play(sound.SHOOT_SOUND)
                if touch_input.is_boosting() and boost.boost_fuel > 0:
                    boost.boost_active = True
                if touch_input.pause_was_pressed():
                    if state == "playing":
                        pre_pause_state = "playing"
                        state = "paused"
                        settings_menu.end_drag()

            player.move(dx, dy)
            player.update_cooldown()

            if keys[pygame.K_SPACE] or left_held:
                new_lazer = player.shoot()
                if new_lazer:
                    lazers.append(new_lazer)
                    sound.play(sound.SHOOT_SOUND)

        if state == "playing":
            spawn_timer += dt_world
            current_interval = max(0.25, spawn_interval - score / 220)
            if spawn_timer >= current_interval:
                spawn_timer = 0.0
                enemies.append(spawn_enemy(settings.WIDTH))

            enemies = [e for e in enemies if e.update_with_dt(dt_world)]
            lazers = [l for l in lazers if l.update(dt_world)]

            if pickup is None:
                pickup_timer -= dt_real
                if pickup_timer <= 0:
                    pickup_timer = random.uniform(7.0, 10.0)
                    x = random.randint(0, settings.WIDTH - 32)
                    pickup = TurboPickup(x, -32)
                    turbo_drops_counter += 1
                    game_particles.spawn_puff(
                        particles, x + 16, -16, (0, 255, 255),
                        count=12, speed_range=(30, 90), size_range=(2, 4),
                        life_range=(0.3, 0.7)
                    )

                    if turbo_drops_counter >= lives_drop_threshold and player.lives < 3:
                        lives_drop_threshold = random.randint(2, 3)
                        lives_drop_timer = random.uniform(1.5, 2.5)

            if lives_pickup is None:
                if lives_drop_timer > 0.0:
                    lives_drop_timer -= dt_real
                    if lives_drop_timer <= 0.0:
                        lives_drop_timer = 0.0
                        if player.lives < 3:
                            x = random.randint(0, settings.WIDTH - 32)
                            lives_pickup = LifePickup(x, -32)
                            turbo_drops_counter = 0
                            game_particles.spawn_puff(
                                particles, x + 16, -16, (255, 200, 0),
                                count=12, speed_range=(30, 90), size_range=(2, 4),
                                life_range=(0.3, 0.7)
                            )
                        else:
                            turbo_drops_counter = 0

            if pickup is not None:
                if not pickup.update_with_dt(dt_world):
                    pickup = None
            if lives_pickup is not None:
                if not lives_pickup.update_with_dt(dt_world):
                    lives_pickup = None

            if pickup is not None and player.colliderect(pickup):
                boost.add_fuel(boost.MAX_FUEL)
                score += 25
                sound.play(sound.PICKUP_SOUND)
                game_particles.spawn_explosion(
                    particles, pickup.x + 16, pickup.y + 16, (0, 255, 255),
                    count=14, speed_range=(50, 180), size_range=(2, 4),
                    life_range=(0.3, 0.7)
                )
                pickup = None

            if lives_pickup is not None and player.colliderect(lives_pickup):
                if player.lives < 3:
                    player.lives += 1
                    sound.play(sound.PICKUP_SOUND)
                game_particles.spawn_explosion(
                    particles, lives_pickup.x + 16, lives_pickup.y + 16,
                    (255, 200, 0), count=14, speed_range=(50, 180),
                    size_range=(2, 4), life_range=(0.3, 0.7)
                )
                lives_pickup = None

            e_rem, l_rem, died, gained = handle_collisions(player, enemies, lazers)
            score += gained * boost.get_kill_score_multiplier()
            enemies = [e for e in enemies if e not in e_rem]
            lazers = [l for l in lazers if l not in l_rem]

            if died:
                state = "gameover"
                enemies.clear()
                lazers.clear()
                pickup = None
                lives_pickup = None
                boost.stop_boost_sound()
                sound.play(sound.GAMEOVER_SOUND)
                sound.stop_music()
                final = int(score)
                save_last_score(final)
                if final > high_score:
                    high_score = final
                    save_high_score(high_score)
                    is_new_high_score = True
                else:
                    is_new_high_score = False

            score += dt_real * 5 * boost.get_passive_score_multiplier()

        particles.update(dt_real)

        const_x, const_y = update_constant_shake()
        hit_x, hit_y = update_hit_feedback()
        boost_x, boost_y = boost.get_boost_shake_offset()
        offset_x = const_x + hit_x + boost_x
        offset_y = const_y + hit_y + boost_y

        screen.fill(BLACK)

        paused_from_title = (state == "paused" and pre_pause_state == "title")

        def _draw_pause_overlay():
            rects = settings_menu.draw_settings_menu(screen, time_elapsed)
            if selected_setting == 0:
                pygame.draw.rect(screen, YELLOW, (settings.WIDTH // 2 - 150, 150, 300, 140), 2)
            elif selected_setting == 1:
                pygame.draw.rect(screen, YELLOW, (settings.WIDTH // 2 - 150, 320, 300, 140), 2)
            elif selected_setting == 2:
                pygame.draw.rect(screen, YELLOW, (settings.WIDTH // 2 - 170, 465, 340, 80), 2)
            elif selected_setting == 3:
                pygame.draw.rect(screen, YELLOW, (settings.WIDTH // 2 - 170, 550, 340, 80), 2)
            return rects

        if state == "title" or paused_from_title:
            draw_title_screen(screen, title_stars, time_elapsed, offset_x, offset_y)
            particles.draw(screen, offset_x, offset_y)
            if state == "paused":
                pause_rects = _draw_pause_overlay()
            else:
                pause_rects = None

        else:
            update_stars_with_dt(stars, dt_world, offset_x, offset_y)

            particles.draw(screen, offset_x, offset_y)

            if state in ("playing", "paused", "gameover"):
                for lazer in lazers:
                    lazer.draw(screen, offset_x, offset_y, time_elapsed)

                for enemy in enemies:
                    draw_asteroid(screen, enemy.x, enemy.y, enemy.visual_size, enemy.color,
                                  offset_x, offset_y, asteroid_id=enemy.asteroid_id)
                    if enemy.hp < enemy.max_hp:
                        bar_w = (enemy.hp / enemy.max_hp) * enemy.visual_size
                        pygame.draw.rect(screen, GREEN,
                                         (enemy.x + offset_x, enemy.y - 6 + offset_y, bar_w, 4))

                if pickup is not None:
                    draw_pickup(screen, pickup, offset_x, offset_y)
                if lives_pickup is not None:
                    draw_life_pickup(screen, lives_pickup, offset_x, offset_y)

            if state in ("playing", "paused"):
                draw_spaceship(screen, player.x, player.y, offset_x, offset_y, moving=is_moving)

            if state in ("playing", "paused"):
                draw_hud(screen, score, player.lives)

            if state == "gameover":
                gameover_rects = draw_game_over(screen, score, high_score, is_new_high_score, time_elapsed)
            else:
                gameover_rects = None

            if state == "paused":
                pause_rects = _draw_pause_overlay()
            else:
                pause_rects = None

        if force_touch_ui and state == "playing":
            touch_ui.draw_touch_ui(screen, touch_input, time_elapsed)

        if state != "playing":
            game_cursor.draw_cursor(screen, mouse_pos)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    asyncio.run(main())
