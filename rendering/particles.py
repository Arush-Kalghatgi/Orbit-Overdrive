# rendering/particles.py
#
# A generic 2D particle system for Orbit Overdrive.
#
# IMPORTANT: All particle coordinates and velocities are in the SAME
# coordinate space as the rest of the game (settings.WIDTH x settings.HEIGHT),
# NOT in virtual (1280x720) space. This is the same coordinate system
# the asteroids, lasers, and player use, so particles will always appear
# at the correct screen position.
#
# Provides:
#   - Particle (data) — one fading dot with position, velocity, color, life
#   - ParticleManager — owns the list of live particles, updates and draws them
#   - spawn_explosion, spawn_sparks, spawn_puff, spawn_player_hit

import math
import random
import pygame
import settings


class Particle:
    """A single fading dot. Position and velocity are in the game's
    current render coordinate space (settings.WIDTH x settings.HEIGHT)."""

    __slots__ = ("x", "y", "vx", "vy", "color", "size", "life", "max_life")

    def __init__(self, x, y, vx, vy, color, size, life):
        self.x = x
        self.y = y
        self.vx = vx          # render pixels per second
        self.vy = vy          # render pixels per second
        self.color = color
        self.size = size      # base radius in render pixels
        self.life = life      # seconds remaining
        self.max_life = life


class ParticleManager:
    def __init__(self):
        self.particles = []

    def clear(self):
        self.particles.clear()

    def add(self, particle):
        self.particles.append(particle)

    def update(self, dt):
        if not self.particles:
            return
        survivors = []
        for p in self.particles:
            p.life -= dt
            if p.life <= 0:
                continue
            p.x += p.vx * dt
            p.y += p.vy * dt
            # Gentle deceleration
            p.vx *= 0.96
            p.vy *= 0.96
            survivors.append(p)
        self.particles = survivors

    def draw(self, surface, offset_x=0, offset_y=0):
        """Draw every live particle. Positions are already in the render
        coordinate space, so we just apply the shake offset — no scaling."""
        if not self.particles:
            return
        for p in self.particles:
            if p.max_life > 0:
                alpha = max(0.0, min(1.0, p.life / p.max_life))
            else:
                alpha = 1.0
            # Size shrinks slightly as the particle fades
            size = max(1, int(p.size * (0.6 + 0.4 * alpha)))
            surf = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
            r, g, b = p.color
            a = int(255 * alpha)
            pygame.draw.circle(surf, (r, g, b, a), (size + 1, size + 1), size)
            surface.blit(surf,
                         (int(p.x + offset_x) - size - 1,
                          int(p.y + offset_y) - size - 1))


# ============================================================
# CONVENIENT SPAWNERS
# ============================================================
#
# Speeds are tuned for a 1280x720 render space. On smaller windows the
# particles will move slightly faster in screen-relative terms, which
# is actually fine — it makes the juice feel snappier on smaller screens.

def spawn_explosion(manager, x, y, color, count=18, speed_range=(60, 220),
                    size_range=(2, 5), life_range=(0.4, 0.9)):
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(*speed_range)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        size = random.uniform(*size_range)
        life = random.uniform(*life_range)
        if random.random() < 0.35:
            c = (255, 230, 150)
        elif random.random() < 0.5:
            c = (255, 180, 80)
        else:
            c = color
        manager.add(Particle(x, y, vx, vy, c, size, life))


def spawn_sparks(manager, x, y, count=6, speed_range=(40, 140),
                 size_range=(1, 2), life_range=(0.15, 0.4)):
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(*speed_range)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        size = random.uniform(*size_range)
        life = random.uniform(*life_range)
        c = (255, 255, 220) if random.random() < 0.5 else (255, 230, 120)
        manager.add(Particle(x, y, vx, vy, c, size, life))


def spawn_puff(manager, x, y, color, count=10, speed_range=(20, 60),
               size_range=(2, 4), life_range=(0.3, 0.6)):
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(*speed_range)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        size = random.uniform(*size_range)
        life = random.uniform(*life_range)
        manager.add(Particle(x, y, vx, vy, color, size, life))


def spawn_player_hit(manager, x, y, count=24, speed_range=(80, 260),
                     size_range=(2, 5), life_range=(0.5, 1.1)):
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(*speed_range)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        size = random.uniform(*size_range)
        life = random.uniform(*life_range)
        if random.random() < 0.5:
            c = (255, 100, 80)
        elif random.random() < 0.7:
            c = (255, 200, 100)
        else:
            c = (255, 255, 255)
        manager.add(Particle(x, y, vx, vy, c, size, life))
