"""
Run a single pong match.

Usage:
    python main.py <left_paddle> <right_paddle>

Where each paddle name is either:
  - "human"           →  keyboard-controlled player
  - a module name     →  a .py file in the paddles/ directory
                         (without the .py extension)

Examples:
    python main.py human chaser           # play against the basic bot
    python main.py human predictor        # play against the prediction bot
    python main.py human example_paddle   # play against the example paddle
    python main.py example_paddle chaser  # watch two AIs play
    python main.py chaser predictor       # watch two built-in bots

Controls (human player):
    Left side:   W = up,  S = down
    Right side:  ↑ = up,  ↓ = down
    ESC          quit

macOS note:
    You may see a harmless OS log message on startup:
        "ApplePersistenceIgnoreState: Existing state will not be touched..."
    To silence it permanently, run once:
        defaults write org.python.python ApplePersistenceIgnoreState YES
"""

import sys
import importlib

import arcade

from engine.paddle import Paddle


def load_paddle_class(name: str) -> type:
    """Resolve a paddle name to a Paddle subclass."""
    if name == "human":
        from paddles.human_paddle import HumanPaddle
        return HumanPaddle

    try:
        module = importlib.import_module(f"paddles.{name}")
    except ModuleNotFoundError:
        print(f"Error: could not find 'paddles/{name}.py'")
        sys.exit(1)

    # Find the first Paddle subclass defined in this module
    candidates = [
        obj for obj in vars(module).values()
        if isinstance(obj, type)
        and issubclass(obj, Paddle)
        and obj is not Paddle
        and obj.__module__ == module.__name__
    ]

    if not candidates:
        print(f"Error: no Paddle subclass found in 'paddles/{name}.py'")
        sys.exit(1)

    return candidates[0]


def main() -> None:
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    left_name, right_name = sys.argv[1], sys.argv[2]
    left_class = load_paddle_class(left_name)
    right_class = load_paddle_class(right_name)

    # Instantiate early to catch errors before opening a window
    from engine.field import Field
    test_field = Field()
    try:
        left_class("left", test_field)._validate_points()
        right_class("right", test_field)._validate_points()
    except (ValueError, TypeError) as e:
        print(f"Paddle error: {e}")
        sys.exit(1)

    from engine.game import PongWindow
    window = PongWindow(left_class, right_class)
    arcade.run()


if __name__ == "__main__":
    main()
