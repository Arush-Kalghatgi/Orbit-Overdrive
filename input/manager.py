# input/manager.py
#
# Touch / mouse input abstraction for Orbit Overdrive.
#
# The InputManager tracks a set of "virtual buttons" (regions on screen
# that respond to touch or mouse clicks). It provides a clean API for
# the game logic to read input without caring whether the input came
# from a finger or a mouse cursor.
#
# Virtual buttons (with their default on-screen positions, set later
# by the rendering layer):
#
#   - JOYSTICK_BASE:    bottom-left corner, large circular region
#   - JOYSTICK_KNOB:    a point inside the joystick base (drag to move)
#   - SHOOT:            bottom-right corner, large circular button
#   - BOOST:            top-right of shoot button, smaller circular button
#   - PAUSE:            top-right corner, small square button
#
# The InputManager doesn't draw anything — that's the touch_ui module's
# job. This module only tracks state.

import pygame


class InputManager:
    """Tracks touch / mouse input on virtual buttons."""

    def __init__(self):
        # Button hit-test rects (set by the touch UI layout)
        self.joystick_base_rect = None   # pygame.Rect for the outer ring
        self.joystick_knob_pos = None    # current knob position (x, y)
        self.shoot_rect = None           # pygame.Rect for shoot button
        self.boost_rect = None           # pygame.Rect for boost button
        self.pause_rect = None           # pygame.Rect for pause button

        # State
        self.shoot_pressed = False       # is the shoot button being held?
        self.boost_pressed = False       # is the boost button being held?
        self.pause_just_pressed = False  # did the pause button get pressed THIS frame?
        self.movement = (0.0, 0.0)       # joystick direction, -1.0 to 1.0 in each axis

        # Internal: which finger / mouse button is on which virtual control
        # -1 means no finger assigned. finger_id is the pygame event finger_id
        # for touch, or 0 for mouse.
        self._shoot_finger = -1
        self._boost_finger = -1
        self._pause_finger = -1
        self._joystick_finger = -1
        self._joystick_start = None      # where the joystick touch started

    # ============================================================
    # Event handling — call this once per frame, before reading state
    # ============================================================
    def handle_events(self, events):
        """Process pygame events and update internal state.
        Works with both touch events (Android/iOS) and mouse events (desktop)."""
        # Reset the "just pressed" flag for pause — it's set to True only
        # on the frame the pause button is first pressed
        self.pause_just_pressed = False

        for event in events:
            # --- Touch events (mobile) ---
            if event.type == pygame.FINGERDOWN:
                self._handle_touch_down(event)
            elif event.type == pygame.FINGERUP:
                self._handle_touch_up(event)
            elif event.type == pygame.FINGERMOTION:
                self._handle_touch_motion(event)

            # --- Mouse events (desktop, for testing) ---
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left click
                    self._handle_pointer_down(event.pos, 0)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self._handle_pointer_up(event.pos, 0)
            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0]:  # left button held
                    self._handle_pointer_motion(event.pos, 0)

    def _handle_touch_down(self, event):
        """event.x, event.y are normalized 0..1 — convert to pixels using
        the current display size."""
        w, h = pygame.display.get_surface().get_size()
        px = int(event.x * w)
        py = int(event.y * h)
        self._handle_pointer_down((px, py), event.finger_id)

    def _handle_touch_up(self, event):
        w, h = pygame.display.get_surface().get_size()
        px = int(event.x * w)
        py = int(event.y * h)
        self._handle_pointer_up((px, py), event.finger_id)

    def _handle_touch_motion(self, event):
        w, h = pygame.display.get_surface().get_size()
        px = int(event.x * w)
        py = int(event.y * h)
        self._handle_pointer_motion((px, py), event.finger_id)

    def _handle_pointer_down(self, pos, finger_id):
        """A pointer (finger or mouse) just touched the screen at pos."""
        # Check each button in priority order. The first match wins.
        if self.shoot_rect and self.shoot_rect.collidepoint(pos):
            self.shoot_pressed = True
            self._shoot_finger = finger_id
        elif self.boost_rect and self.boost_rect.collidepoint(pos):
            self.boost_pressed = True
            self._boost_finger = finger_id
        elif self.pause_rect and self.pause_rect.collidepoint(pos):
            self.pause_just_pressed = True
            self._pause_finger = finger_id
        elif self.joystick_base_rect and self.joystick_base_rect.collidepoint(pos):
            # Joystick touch — record where the touch started, and set
            # the knob to that position. As the finger drags, the knob
            # follows (clamped to the base radius).
            self._joystick_finger = finger_id
            self._joystick_start = pos
            self._update_joystick_knob(pos)

    def _handle_pointer_up(self, pos, finger_id):
        """A pointer was lifted. Release any virtual button it was on."""
        if finger_id == self._shoot_finger:
            self.shoot_pressed = False
            self._shoot_finger = -1
        if finger_id == self._boost_finger:
            self.boost_pressed = False
            self._boost_finger = -1
        if finger_id == self._pause_finger:
            self._pause_finger = -1
        if finger_id == self._joystick_finger:
            self._joystick_finger = -1
            self._joystick_start = None
            self.movement = (0.0, 0.0)
            self.joystick_knob_pos = None

    def _handle_pointer_motion(self, pos, finger_id):
        """A pointer moved while held. Update the joystick knob if this
        finger is the one on the joystick."""
        if finger_id == self._joystick_finger:
            self._update_joystick_knob(pos)

    def _update_joystick_knob(self, pos):
        """Move the joystick knob to a new position, clamped to the base
        circle, and update the movement vector."""
        if self.joystick_base_rect is None:
            return
        # Center of the joystick base
        base_cx = self.joystick_base_rect.centerx
        base_cy = self.joystick_base_rect.centery
        # Maximum distance the knob can be from the center
        max_dist = self.joystick_base_rect.width // 2 - 8  # 8px padding
        # Vector from base center to finger
        dx = pos[0] - base_cx
        dy = pos[1] - base_cy
        dist = (dx * dx + dy * dy) ** 0.5
        if dist > max_dist and dist > 0:
            # Clamp to the edge of the base
            scale = max_dist / dist
            dx *= scale
            dy *= scale
        knob_x = base_cx + dx
        knob_y = base_cy + dy
        self.joystick_knob_pos = (knob_x, knob_y)
        # Normalized movement vector (-1.0 to 1.0)
        self.movement = (dx / max_dist if max_dist > 0 else 0.0,
                         dy / max_dist if max_dist > 0 else 0.0)

    # ============================================================
    # Layout — called by the touch UI module once per frame
    # ============================================================
    def set_layout(self, joystick_base, joystick_knob,
                   shoot, boost, pause):
        """Set the on-screen positions of all virtual buttons.
        Called by rendering/touch_ui.py after it computes the layout."""
        self.joystick_base_rect = joystick_base
        self.joystick_knob_pos = joystick_knob
        self.shoot_rect = shoot
        self.boost_rect = boost
        self.pause_rect = pause

    # ============================================================
    # Public API — the game logic calls these
    # ============================================================
    def get_movement(self):
        """Return the joystick direction as a tuple (x, y),
        each component in the range -1.0 to 1.0."""
        return self.movement

    def is_shooting(self):
        return self.shoot_pressed

    def is_boosting(self):
        return self.boost_pressed

    def pause_was_pressed(self):
        """True on the single frame the pause button is first pressed.
        Game logic should check this and immediately set state to paused."""
        return self.pause_just_pressed
