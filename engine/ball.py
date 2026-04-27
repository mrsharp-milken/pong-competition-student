import math
import random


class Ball:
    """
    The pong ball. Passed to paddle tick() and lifecycle hooks so strategies
    can read position and velocity.

    Treat this as read-only inside your paddle — the engine owns movement.

    You may construct Ball objects with explicit state for prediction purposes:
        Ball(x, y, dx, dy)
    """

    RADIUS: float = 8
    INITIAL_SPEED: float = 5.0
    MAX_SPEED: float = 18.0

    def __init__(self, x: float = 0.0, y: float = 0.0,
                 dx: float = 0.0, dy: float = 0.0):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy

    @property
    def speed(self) -> float:
        """Current magnitude of the ball's velocity."""
        return math.sqrt(self.dx ** 2 + self.dy ** 2)

    def update(self) -> None:
        """Advance the ball by one frame. Bouncing is handled separately by the engine."""
        self.x += self.dx
        self.y += self.dy

    def _clamp_speed(self) -> None:
        """Keep ball speed within the allowed maximum."""
        current = self.speed
        if current > self.MAX_SPEED:
            scale = self.MAX_SPEED / current
            self.dx *= scale
            self.dy *= scale
