from abc import ABC, abstractmethod

from engine.ball import Ball
from engine.field import Field


class OpponentView:
    """
    A read-only window into the opponent's paddle.

    You can observe the opponent's position and size, but you cannot
    access their private state or strategy. This is information hiding.

    Passed to tick() and lifecycle hooks as the `opponent` argument.
    """

    def __init__(self, paddle: "Paddle"):
        self._paddle = paddle

    def get_x(self) -> float:
        """The opponent's x position (fixed for the whole match)."""
        return self._paddle.get_x()

    def get_y(self) -> float:
        """The opponent's current y position."""
        return self._paddle.get_y()

    def get_length(self) -> float:
        """The opponent's paddle height in pixels."""
        return self._paddle.length


class Paddle(ABC):
    """
    Abstract base class for all pong paddles.

    This class cannot be instantiated directly. Every paddle in the game is
    a concrete subclass that inherits from Paddle and overrides tick().
    The engine calls tick() every frame and you supply the behaviour inside it.

    Your paddle IS-A Paddle and reuses all the movement, validation, and
    lifecycle machinery defined here without having to rewrite it.

    To create your own paddle, subclass this and:
      1. Define NAME as a class variable.
      2. Override __init__ to call super().__init__() then set your stats.
      3. Override tick() to move your paddle each frame.
      4. Optionally override any lifecycle hooks.
    """

    # Class variables — shared by ALL instances of the class, not tied to any
    # individual object. The tournament reads Paddle.NAME without ever creating
    # a paddle instance.

    NAME: str = "Unnamed"
    """Override this in your subclass with your paddle's display name."""

    POINT_BUDGET: int = 10
    """Total points every paddle may spend upgrading stats above their defaults."""

    DEFAULTS: dict = {
        "length":    60.0,   # pixels
        "max_speed":  5.0,   # pixels per frame
        "curve":      1.0,   # edge-hit angle deflection multiplier
        "bounce":     1.0,   # centre-hit speed boost multiplier
    }
    """
    Default stat values before any upgrades.
    Each point spent on a stat adds 1.0 to it above this baseline.
    The engine reads these to check that your total spending is within budget.
    """

    WIDTH: float = 12.0
    """Visual and collision width of the paddle in pixels."""

    def __init__(self, side: str, field: Field) -> None:
        """
        Initialise the paddle's position and default stats.

        side:  "left" or "right"
        field: the Field instance (read its dimensions; do not modify it)

        When you override __init__ in your subclass, always call
        super().__init__(side, field) first so that defaults are set,
        then override whichever stats you want to upgrade.
        """
        self.side: str = side
        self._field: Field = field

        # Private position — access only through get_x() / get_y() / set_y().
        # The double underscore triggers Python name-mangling: self.__x becomes
        # self._Paddle__x, so subclasses cannot accidentally read or write it.
        self.__x: float = field.left_paddle_x if side == "left" else field.right_paddle_x
        self.__y: float = field.height / 2.0

        # Instance variables — each paddle object has its own copy of these.
        # Override any of these in your __init__ after calling super().__init__().
        self.length:    float = self.DEFAULTS["length"]
        self.max_speed: float = self.DEFAULTS["max_speed"]
        self.curve:     float = self.DEFAULTS["curve"]
        self.bounce:    float = self.DEFAULTS["bounce"]

    # --- Position getters and setter (encapsulation) ---

    def get_x(self) -> float:
        """Return the paddle's x position. X is fixed for the whole match."""
        return self.__x

    def get_y(self) -> float:
        """Return the paddle's current y position."""
        return self.__y

    def set_y(self, value: float) -> None:
        """
        Move the paddle to a new y position.

        Rules enforced by this method:
          - You may not move more than self.max_speed pixels per call.
            Violating this raises a ValueError — it is a programming error.
          - The paddle is silently clamped to stay within the field boundaries.
            This is a physical constraint, not a programming error.

        Typical usage in tick():
            if ball.y > self.get_y():
                self.set_y(self.get_y() + self.max_speed)
            elif ball.y < self.get_y():
                self.set_y(self.get_y() - self.max_speed)
        """
        delta = abs(value - self.__y)
        if delta > self.max_speed + 1e-9:
            raise ValueError(
                f"{self.__class__.__name__}.set_y(): tried to move {delta:.1f}px "
                f"in one frame, but max_speed is {self.max_speed:.1f}px. "
                f"Move at most self.max_speed per call."
            )
        half = self.length / 2.0
        self.__y = max(half, min(self._field.height - half, float(value)))

    # --- Abstract method — subclasses MUST override this ---

    @abstractmethod
    def tick(self, ball: Ball, field: Field, opponent: OpponentView) -> None:
        """
        Called every frame by the engine. Move your paddle here.

        ball:     the ball's current position, velocity, and prediction method
        field:    board dimensions and current scores
        opponent: read-only view of the opponent's position and size

        At minimum, call set_y() to move your paddle:
            self.set_y(self.get_y() + self.max_speed)

        You may not move more than self.max_speed pixels per frame.
        """

    # --- Lifecycle hooks — subclasses MAY override these ---

    def on_game_start(self) -> None:
        """Called once before the first point. Initialise any strategy state here."""

    def on_ball_approach(self, ball: Ball) -> None:
        """
        Called when the ball starts heading toward your side.
        Fires once per approach (not every frame).
        Good place to store a planned destination in an instance variable,
        which tick() can then move toward incrementally.
        """

    def on_ball_leaving(self, ball: Ball) -> None:
        """Called right after your paddle hits the ball and it heads away."""

    def on_opponent_scored(self) -> None:
        """Called when the opponent scores a point."""

    def on_you_scored(self) -> None:
        """Called when you score a point."""

    # --- Convenience properties ---

    @property
    def my_score(self) -> int:
        """Your current score in the match."""
        return self._field.left_score if self.side == "left" else self._field.right_score

    @property
    def opponent_score(self) -> int:
        """The opponent's current score in the match."""
        return self._field.right_score if self.side == "left" else self._field.left_score

    # --- Engine-internal validation — do not call or override ---

    def _validate_points(self) -> None:
        """
        Check that this paddle's stats are within the rules:
          1. No stat may be set below its default value — defaults are minimums.
          2. The total points spent (sum of all increases above defaults) must
             not exceed POINT_BUDGET.

        Called by the engine before the game starts. Raises ValueError if
        either rule is broken.
        """
        for attr, default in self.DEFAULTS.items():
            value = getattr(self, attr)
            if value < default:
                raise ValueError(
                    f"{self.__class__.__name__}.{attr} is {value:.1f}, which is "
                    f"below the minimum of {default:.1f}. "
                    f"Stats can only be increased above their defaults, not reduced."
                )
        spent = sum(
            getattr(self, attr) - default
            for attr, default in self.DEFAULTS.items()
        )
        if spent > self.POINT_BUDGET:
            raise ValueError(
                f"{self.__class__.__name__} spent {spent:.0f} points "
                f"but the budget is {self.POINT_BUDGET}. "
                f"Reduce your stat upgrades in __init__."
            )
