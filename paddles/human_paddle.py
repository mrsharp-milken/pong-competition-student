import arcade

from engine.paddle import Paddle


class HumanPaddle(Paddle):
    """
    A human-controlled paddle. Movement is driven by keyboard input rather
    than a strategy algorithm.

    Left side:  W (up)  /  S (down)
    Right side: ↑ (up)  /  ↓ (down)

    This paddle is excluded from the tournament because it needs a human operator.
    Use it with main.py to play against any AI paddle:

        python main.py human chaser
        python main.py human my_paddle
    """

    NAME = "Human"
    TOURNAMENT = False  # tells tournament.py to skip this file

    def __init__(self, side, field):
        super().__init__(side, field)
        self._keys = set()

    def tick(self, ball, field, opponent) -> None:
        if self.side == "left":
            up_key, down_key = arcade.key.W, arcade.key.S
        else:
            up_key, down_key = arcade.key.UP, arcade.key.DOWN

        if up_key in self._keys:
            self.set_y(self.get_y() + self.max_speed)
        elif down_key in self._keys:
            self.set_y(self.get_y() - self.max_speed)

    def on_key_press(self, key: int) -> None:
        self._keys.add(key)

    def on_key_release(self, key: int) -> None:
        self._keys.discard(key)
