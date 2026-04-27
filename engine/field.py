from engine.ball import Ball


class Field:
    """
    Represents the game board. Passed to paddle tick() and lifecycle hooks
    so strategies can read scores, board dimensions, and predict ball paths.

    Treat this as read-only inside your paddle — the engine owns the scores.
    """

    WIDTH = 800
    HEIGHT = 600
    X_OFFSET = 40.0   # how far in from each edge the paddle face is placed

    def __init__(self):
        self.left_score: int = 0
        self.right_score: int = 0

    @property
    def width(self) -> int:
        return self.WIDTH

    @property
    def height(self) -> int:
        return self.HEIGHT

    @property
    def left_paddle_x(self) -> float:
        """X position of the left paddle face."""
        return self.X_OFFSET

    @property
    def right_paddle_x(self) -> float:
        """X position of the right paddle face."""
        return self.WIDTH - self.X_OFFSET

    def get_next_collision(self, ball: Ball) -> tuple[float, float]:
        """
        Given a ball's current position and velocity, return the (x, y) of the
        next collision it will have — either a top/bottom wall bounce or arrival
        at the approaching paddle face.

        Collision targets:
          Top wall    — y = Ball.RADIUS
          Bottom wall — y = height - Ball.RADIUS
          Left face   — x = left_paddle_x  (when ball is moving left)
          Right face  — x = right_paddle_x (when ball is moving right)

        If the ball is not moving horizontally (dx == 0), returns the current
        position unchanged.
        """
        if ball.dx == 0:
            return (ball.x, ball.y)

        y_top = Ball.RADIUS
        y_bot = self.HEIGHT - Ball.RADIUS

        target_x = self.right_paddle_x if ball.dx > 0 else self.left_paddle_x
        steps_to_paddle = (target_x - ball.x) / ball.dx

        if ball.dy == 0:
            return (target_x, ball.y)

        # Steps to nearest horizontal wall
        if ball.dy < 0:
            steps_to_wall = (y_top - ball.y) / ball.dy
            wall_y = y_top
        else:
            steps_to_wall = (y_bot - ball.y) / ball.dy
            wall_y = y_bot

        if steps_to_wall < steps_to_paddle:
            hit_x = ball.x + ball.dx * steps_to_wall
            return (hit_x, wall_y)
        else:
            hit_y = ball.y + ball.dy * steps_to_paddle
            return (target_x, hit_y)
