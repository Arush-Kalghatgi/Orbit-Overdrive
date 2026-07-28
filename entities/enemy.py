import random
import pygame
import settings
from settings import DARK_BROWN, MEDIUM_GRAY, DARK_GRAY


# Counter for assigning unique IDs to asteroids
_next_asteroid_id = 0


class Enemy(pygame.Rect):
    def __init__(self, x, y, speed, hp, color, visual_size, asteroid_id):
        super().__init__(x, y, visual_size, visual_size)
        self.speed = speed
        self.hp = hp
        self.max_hp = hp
        self.color = color
        self.visual_size = visual_size
        self.asteroid_id = asteroid_id

    def update_with_dt(self, dt):
        self.y += self.speed * dt * 60
        return self.y < settings.HEIGHT

    def take_damage(self):
        self.hp -= 1
        return self.hp <= 0


def _new_id():
    global _next_asteroid_id
    _next_asteroid_id += 1
    return _next_asteroid_id


def spawn_enemy(width):
    x = random.randint(0, width - 70)
    
    roll = random.random()
    if roll < 0.4:
        # Big slow rocky asteroid
        size = random.randint(50, 65)
        speed = random.uniform(1.5, 2.3)
        hp = 3
        return Enemy(x, -size, speed, hp, DARK_BROWN, size, _new_id())
    elif roll < 0.7:
        # Medium rock
        size = random.randint(38, 50)
        speed = random.uniform(2.5, 3.5)
        hp = 2
        return Enemy(x, -size, speed, hp, MEDIUM_GRAY, size, _new_id())
    else:
        # Small fast rock
        size = random.randint(25, 38)
        speed = random.uniform(4.0, 5.5)
        hp = 1
        return Enemy(x, -size, speed, hp, DARK_GRAY, size, _new_id())