import pygame
import settings
from entities.bullet import Lazer


class Player(pygame.Rect):
    def __init__(self, speed):
        super().__init__(settings.WIDTH // 2 - 20, settings.HEIGHT - 50, 40, 40)
        self.base_speed = speed
        self.cooldown = 0
        self.lives = 3

    def move(self, dx, dy, speed_multiplier=1.0):
        """Move the player. dx/dy are unit directions (-1, 0, 1)."""
        actual_dx = int(dx * self.base_speed * speed_multiplier)
        actual_dy = int(dy * self.base_speed * speed_multiplier)
        
        new_x = self.x + actual_dx
        new_y = self.y + actual_dy
        if 0 <= new_x <= settings.WIDTH - self.width:
            self.x = new_x
        if 0 <= new_y <= settings.HEIGHT - self.height:
            self.y = new_y

    def shoot(self):
        if self.cooldown <= 0:
            self.cooldown = 15
            return Lazer(self.x + self.width // 2 - 2, self.y)
        return None

    def update_cooldown(self):
        if self.cooldown > 0:
            self.cooldown -= 1