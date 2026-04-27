import math
import random

from engine.ball import Ball
from engine.field import Field
from engine.paddle import OpponentView, Paddle


class PongSimulator:
    """
    Headless pong physics engine.

    Used by the tournament runner (no display needed) and wrapped by
    PongWindow (arcade) for the visual game. All game logic lives here.

    PongSimulator HAS-A Ball (it creates and owns the ball) and
    HAS-A Field (passed around to paddles; could exist independently).
    """

    POINTS_TO_WIN: int = 7
    MAX_FRAMES: int = 18_000  # safety valve: ~5 min at 60 fps

    # Curve and bounce scaling constants
    CURVE_SCALE: float = 0.6    # dy added per point of curve at paddle edge
    BOUNCE_SCALE: float = 0.05  # fractional speed boost per point of bounce at centre
    RALLY_SPEED_INCREASE: float = 0.05  # ball gets 5% faster after every paddle hit

    def __init__(self, left_paddle_class: type, right_paddle_class: type):
        self.field = Field()
        self.ball = Ball()
        self.left_paddle: Paddle = left_paddle_class("left", self.field)
        self.right_paddle: Paddle = right_paddle_class("right", self.field)

        self.game_over: bool = False
        self._frame: int = 0

        # Track ball direction to detect approach events
        self._last_dx_sign: int = 0

        self._reset_ball()

    def start(self) -> None:
        """
        Initialise the match: validate point budgets, fire on_game_start,
        and dispatch the first on_ball_approach.
        """
        self.left_paddle._validate_points()
        self.right_paddle._validate_points()

        self.left_paddle.on_game_start()
        self.right_paddle.on_game_start()
        self._last_dx_sign = self._dx_sign()
        self._dispatch_approach()

    def step(self) -> None:
        """Advance the simulation by one frame."""
        if self.game_over:
            return

        self._frame += 1

        left_view = OpponentView(self.right_paddle)
        right_view = OpponentView(self.left_paddle)

        self.left_paddle.tick(self.ball, self.field, left_view)
        self.right_paddle.tick(self.ball, self.field, right_view)

        self.ball.update()
        self._bounce_ball()

        self._check_paddle_collision(self.left_paddle)
        self._check_paddle_collision(self.right_paddle)

        # Fire on_ball_approach if direction reversed after a paddle hit
        current_sign = self._dx_sign()
        if current_sign != self._last_dx_sign:
            self._last_dx_sign = current_sign
            self._dispatch_approach()

        self._check_scoring()

        if self._frame >= self.MAX_FRAMES:
            self.game_over = True

    def run(self) -> tuple[int, int]:
        """
        Run the full match to completion without rendering.
        Returns (left_score, right_score).
        """
        self.start()
        while not self.game_over:
            self.step()
        return self.field.left_score, self.field.right_score

    # ------------------------------------------------------------------

    def _reset_ball(self) -> None:
        """Respawn ball at centre with a random direction."""
        self.ball.x = self.field.width / 2
        self.ball.y = self.field.height / 2

        angle = random.uniform(-math.pi / 5, math.pi / 5)
        direction = random.choice([-1, 1])
        self.ball.dx = direction * Ball.INITIAL_SPEED * math.cos(angle)
        self.ball.dy = Ball.INITIAL_SPEED * math.sin(angle)

    def _bounce_ball(self) -> None:
        """Reflect the ball off the top and bottom walls."""
        if self.ball.y - Ball.RADIUS <= 0:
            self.ball.y = Ball.RADIUS
            self.ball.dy = abs(self.ball.dy)
        elif self.ball.y + Ball.RADIUS >= self.field.height:
            self.ball.y = self.field.height - Ball.RADIUS
            self.ball.dy = -abs(self.ball.dy)

    def _dx_sign(self) -> int:
        if self.ball.dx > 0:
            return 1
        if self.ball.dx < 0:
            return -1
        return 0

    def _dispatch_approach(self) -> None:
        if self.ball.dx < 0:
            self.left_paddle.on_ball_approach(self.ball)
        elif self.ball.dx > 0:
            self.right_paddle.on_ball_approach(self.ball)

    def _check_paddle_collision(self, paddle: Paddle) -> None:
        ball = self.ball
        half_len = paddle.length / 2
        half_w = paddle.WIDTH / 2
        paddle_x = paddle.get_x()
        paddle_y = paddle.get_y()

        # Broad check: ball must overlap the paddle's bounding box
        if not (
            abs(ball.x - paddle_x) <= half_w + ball.RADIUS
            and abs(ball.y - paddle_y) <= half_len + ball.RADIUS
        ):
            return

        # Only process the collision if the ball is moving toward this paddle
        if paddle.side == "left" and ball.dx >= 0:
            return
        if paddle.side == "right" and ball.dx <= 0:
            return

        # --- Reflect ---
        hit_offset = ball.y - paddle_y                    # +ve = top half of paddle
        normalized = hit_offset / max(half_len, 1)        # −1..+1

        # Reverse horizontal direction
        ball.dx = abs(ball.dx) if paddle.side == "left" else -abs(ball.dx)

        # Curve: edge hits deflect the angle more sharply
        ball.dy += paddle.curve * self.CURVE_SCALE * normalized

        # Natural rally speed increase: every hit makes the ball a little faster
        rally_mult = 1.0 + self.RALLY_SPEED_INCREASE
        ball.dx *= rally_mult
        ball.dy *= rally_mult

        ball._clamp_speed()

        # Bounce: centre hits add speed (after clamping speed)
        centre_factor = 1.0 - abs(normalized)
        speed_mult = 1.0 + paddle.bounce * self.BOUNCE_SCALE * centre_factor
        ball.dx *= speed_mult
        ball.dy *= speed_mult

        # Push ball clear of the paddle face to avoid double-hit
        if paddle.side == "left":
            ball.x = paddle_x + half_w + ball.RADIUS + 1
        else:
            ball.x = paddle_x - half_w - ball.RADIUS - 1

        paddle.on_ball_leaving(ball)

        # Update direction tracking so we fire on_ball_approach correctly
        self._last_dx_sign = self._dx_sign()

    def _check_scoring(self) -> None:
        scored = False

        if self.ball.x - self.ball.RADIUS < 0:
            # Ball passed the left edge: right player scores
            self.field.right_score += 1
            self.right_paddle.on_you_scored()
            self.left_paddle.on_opponent_scored()
            scored = True
        elif self.ball.x + self.ball.RADIUS > self.field.width:
            # Ball passed the right edge: left player scores
            self.field.left_score += 1
            self.left_paddle.on_you_scored()
            self.right_paddle.on_opponent_scored()
            scored = True

        if scored:
            if (self.field.left_score >= self.POINTS_TO_WIN
                    or self.field.right_score >= self.POINTS_TO_WIN):
                self.game_over = True
            else:
                self._reset_ball()
                self._last_dx_sign = self._dx_sign()
                self._dispatch_approach()
