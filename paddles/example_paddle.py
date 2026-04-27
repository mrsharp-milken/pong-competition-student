"""
Pong Competition — Student Paddle Template

STEP 1: Copy this file and rename it   e.g.  alice_paddle.py
STEP 2: Rename the class inside        e.g.  class AlicePaddle(Paddle)
STEP 3: Fill in NAME, set your stats in __init__, and write your tick() logic.
STEP 4: Test it:   python main.py example_paddle chaser
STEP 5: Enter the tournament!

See getting_started.md for more information.
"""

from engine.ball import Ball
from engine.paddle import Paddle


class ExamplePaddle(Paddle):
    """Replace this docstring with a description of your paddle's strategy."""

    NAME = "Example"   # TODO: change this

    def __init__(self, side, field):
        super().__init__(side, field)

        # TODO: spend your 10 points adding points to these four stats.
        self.length    = 60.0
        self.max_speed =  5.0
        self.curve     =  1.0
        self.bounce    =  1.0

    def on_game_start(self) -> None:
        """Called once before the first point. Initialise your state here."""
        self.rally_count = 0

    def on_ball_approach(self, ball) -> None:
        """Ball is heading toward you. Fires once per approach, not every frame."""
        pass

    def on_ball_leaving(self, ball) -> None:
        """Ball just left your paddle."""
        self.rally_count += 1

    def on_opponent_scored(self) -> None:
        self.rally_count = 0

    def on_you_scored(self) -> None:
        self.rally_count = 0

    def tick(self, ball, field, opponent) -> None:
        """
        Called every frame by the engine. Move your paddle here.

        Use set_y() to move. You may not exceed self.max_speed per call.
        Use get_y() to read your current position.

        TODO: replace this simple example with your own strategy.
        """
        # Simple example: chase the ball's current y position directly.
        if ball.y > self.get_y():
            self.set_y(self.get_y() + 2)
