import pygame
import settings


class Lazer(pygame.Rect):
    def __init__(self, x, y):
        super().__init__(x, y, 6, 20)   # 6 wide, 20 tall — visible bullets
        # Speed in "pixels per frame at 60 FPS" (so the math is simple)
        self.speed = -15                  # = 900 pixels/second, fast & visible

    def update(self, dt=1.0):
        """Move the bullet. dt is the frame-time fraction.
        When dt = 1.0/60, the bullet moves self.speed pixels.
        During turbo, dt_world = 3.0/60 = 0.05, so it moves 3x faster."""
        self.y += self.speed * dt * 60   # *60 converts dt-seconds to per-frame
        return self.y > 0