import pygame
import math
import random
import settings


class Lazer(pygame.Rect):
    """A laser projectile drawn as a small chunky projectile.
    
    The collision box is a 6x20 rectangle (same as before, so gameplay
    is unchanged). What you SEE is a brighter, layered projectile with
    a pulsing core, a magenta body, a cyan outer glow, and a white
    "tip" pixel at the front."""
    
    def __init__(self, x, y):
        super().__init__(x, y, 6, 20)
        self.speed = -15
        # Per-projectile visual variation so they don't all look identical
        self._pulse_offset = random.uniform(0, math.tau)
        # Pre-render the projectile so it draws fast (one blit per frame)
        self._sprite = self._build_sprite()
    
    def _build_sprite(self):
        """Build a single projectile sprite on a transparent surface.
        The sprite is 8 wide and 22 tall (a few pixels larger than the
        collision box so the visual can have a small glow halo)."""
        w, h = 8, 22
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        
        # Colors
        CORE_WHITE = (255, 255, 255)
        HOT_MAGENTA = (255, 80, 220)        # inner body
        COOL_PURPLE = (160, 60, 200)        # outer body
        CYAN_HALO = (140, 230, 255)         # outer glow
        DARK_PURPLE = (80, 20, 110)         # shadow edge
        
        cx = w // 2
        # The "tip" of the laser points UP (since it travels upward)
        tip_y = 1
        base_y = h - 2
        
        # --- Outer cyan glow halo (largest, softest) ---
        # A wide soft rectangle that extends past the body, giving a glow feel
        glow_rect = pygame.Rect(0, tip_y - 1, w, h - 2)
        # Slightly tapered — narrower at the tip, wider at the base
        glow_points = [
            (cx - 1, tip_y - 1),    # narrow at tip
            (cx + 1, tip_y - 1),
            (w - 1, base_y),        # wider at base
            (0, base_y),
        ]
        # Draw the glow with a translucent color (semi-transparent)
        GLOW_SURF = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.polygon(GLOW_SURF, (*CYAN_HALO, 90), glow_points)
        surf.blit(GLOW_SURF, (0, 0))
        
        # --- Outer body (cool purple, tapered) ---
        # A trapezoid that's slightly narrower at the tip
        outer_points = [
            (cx - 1, tip_y),         # tip-left
            (cx + 1, tip_y),         # tip-right
            (cx + 2, base_y - 1),    # base-right
            (cx - 2, base_y - 1),    # base-left
        ]
        pygame.draw.polygon(surf, COOL_PURPLE, outer_points)
        
        # --- Inner body (hot magenta) ---
        inner_points = [
            (cx, tip_y + 1),
            (cx + 1, tip_y + 1),
            (cx + 1, base_y - 3),
            (cx, base_y - 3),
        ]
        pygame.draw.polygon(surf, HOT_MAGENTA, inner_points)
        
        # --- White core (the bright "hot" center) ---
        core_points = [
            (cx, tip_y + 2),
            (cx, base_y - 6),
        ]
        # Draw as a thin vertical line in pure white
        pygame.draw.line(surf, CORE_WHITE, (cx, tip_y + 2), (cx, base_y - 5), 1)
        
        # --- White tip pixel (the "leading edge" indicator) ---
        # A bright pixel right at the tip so the laser reads as moving up
        pygame.draw.circle(surf, CORE_WHITE, (cx, tip_y + 1), 1)
        # A small magenta cap on the tip
        pygame.draw.circle(surf, HOT_MAGENTA, (cx, tip_y + 2), 1)
        
        # --- Dark edge on the base (suggests depth / where the laser was fired from) ---
        pygame.draw.line(surf, DARK_PURPLE, (cx - 2, base_y - 1), (cx + 2, base_y - 1), 1)
        
        return surf
    
    def update(self, dt=1.0):
        """Move the bullet. dt is the frame-time fraction.
        When dt = 1.0/60, the bullet moves self.speed pixels.
        During turbo, dt_world = 3.0/60 = 0.05, so it moves 3x faster."""
        self.y += self.speed * dt * 60
        return self.y > 0
    
    def draw(self, surface, offset_x=0, offset_y=0, time_elapsed=0.0):
        """Draw the laser sprite at the projectile's position.
        The sprite is drawn centered horizontally on the collision rect,
        and the vertical position is aligned so the tip is at the top
        of the collision rect.
        
        A subtle brightness pulse is applied via alpha modulation so
        different lasers look slightly different over time."""
        # Pulse: brightness oscillates 0.85x to 1.0x over a ~0.3s cycle
        # Each laser has a random phase so they don't pulse in sync
        pulse = 0.925 + 0.075 * math.sin(time_elapsed * 18 + self._pulse_offset)
        
        # We want the sprite centered on the rect's x, and the tip of
        # the sprite aligned with the top of the rect.
        sprite_w, sprite_h = self._sprite.get_size()
        # The rect is 6 wide. The sprite is 8 wide. Center the sprite
        # horizontally on the rect's center.
        blit_x = self.x + self.width // 2 - sprite_w // 2 + offset_x
        # The rect's top is at self.y. The sprite's tip is at the top
        # of the sprite, so align the sprite's top with the rect's top.
        blit_y = self.y + offset_y
        
        # Apply pulse by drawing the sprite onto a temp surface and
        # modulating its alpha
        if pulse < 0.99:
            # Create a per-frame surface to allow alpha modulation
            temp = self._sprite.copy()
            # Apply alpha to all pixels
            alpha = int(255 * pulse)
            temp.set_alpha(alpha)
            surface.blit(temp, (blit_x, blit_y))
        else:
            surface.blit(self._sprite, (blit_x, blit_y))
