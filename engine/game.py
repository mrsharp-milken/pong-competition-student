import arcade

from engine.simulator import PongSimulator


# Colours
_WHITE = arcade.color.WHITE
_BLACK = arcade.color.BLACK
_GRAY = (80, 80, 80)
_YELLOW = arcade.color.YELLOW
_GREEN = (100, 220, 100)
_RED = (220, 100, 100)


class PongWindow(arcade.Window):
    """
    Visual pong game window. Wraps PongSimulator and adds arcade rendering.

    Create an instance then call arcade.run() to start the event loop.
    """

    def __init__(self, left_paddle_class: type, right_paddle_class: type):
        self._sim = PongSimulator(left_paddle_class, right_paddle_class)
        field = self._sim.field
        super().__init__(field.width, field.height, "Pong Competition")
        self.background_color = _BLACK
        self._sim.start()
        self._left_name = getattr(left_paddle_class, "NAME", left_paddle_class.__name__)
        self._right_name = getattr(right_paddle_class, "NAME", right_paddle_class.__name__)

        cx = field.width / 4
        self._left_score_text = arcade.Text(
            "0", cx, field.height - 55,
            _WHITE, font_size=40, anchor_x="center",
        )
        self._right_score_text = arcade.Text(
            "0", field.width - cx, field.height - 55,
            _WHITE, font_size=40, anchor_x="center",
        )
        self._left_name_text = arcade.Text(
            self._left_name, field.width / 4, 12,
            _GRAY, font_size=11, anchor_x="center",
        )
        self._right_name_text = arcade.Text(
            self._right_name, field.width * 3 / 4, 12,
            _GRAY, font_size=11, anchor_x="center",
        )
        self._winner_text = arcade.Text(
            "", field.width / 2, field.height / 2,
            _GREEN, font_size=36, anchor_x="center", anchor_y="center",
        )
        self._esc_text = arcade.Text(
            "press ESC to exit",
            field.width / 2, field.height / 2 - 34,
            _GRAY, font_size=13, anchor_x="center", anchor_y="center",
        )

    # ------------------------------------------------------------------
    # arcade callbacks
    # ------------------------------------------------------------------

    def on_update(self, delta_time: float) -> None:
        self._sim.step()

    def on_draw(self) -> None:
        self.clear()

        sim = self._sim
        field = sim.field

        self._draw_center_line(field)
        self._draw_paddle(sim.left_paddle)
        self._draw_paddle(sim.right_paddle)
        self._draw_ball(sim.ball)
        self._draw_scores(field)
        self._draw_names(field)

        if sim.game_over:
            self._draw_winner(field)

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------

    def _draw_center_line(self, field) -> None:
        dash_height = 14
        gap = 10
        x = field.width / 2
        y = gap
        while y < field.height:
            arcade.draw_line(x, y, x, min(y + dash_height, field.height), _GRAY, 2)
            y += dash_height + gap

    def _draw_paddle(self, paddle) -> None:
        arcade.draw_rect_filled(
            arcade.XYWH(paddle.get_x(), paddle.get_y(), paddle.WIDTH, paddle.length),
            _WHITE,
        )

    def _draw_ball(self, ball) -> None:
        arcade.draw_circle_filled(ball.x, ball.y, ball.RADIUS, _WHITE)

    def _draw_scores(self, field) -> None:
        self._left_score_text.text = str(field.left_score)
        self._left_score_text.draw()
        self._right_score_text.text = str(field.right_score)
        self._right_score_text.draw()

    def _draw_names(self, field) -> None:
        self._left_name_text.draw()
        self._right_name_text.draw()

    def _draw_winner(self, field) -> None:
        winner = self._left_name if field.left_score > field.right_score else self._right_name

        arcade.draw_rect_filled(
            arcade.XYWH(field.width / 2, field.height / 2, 420, 90),
            (0, 0, 0, 200),
        )
        self._winner_text.text = f"{winner} wins!"
        self._winner_text.draw()
        self._esc_text.draw()

    def on_key_press(self, key: int, modifiers: int) -> None:  # type: ignore[override]
        if key == arcade.key.ESCAPE:
            self.close()
            return
        for paddle in (self._sim.left_paddle, self._sim.right_paddle):
            if hasattr(paddle, "on_key_press"):
                paddle.on_key_press(key)

    def on_key_release(self, key: int, modifiers: int) -> None:  # type: ignore[override]
        for paddle in (self._sim.left_paddle, self._sim.right_paddle):
            if hasattr(paddle, "on_key_release"):
                paddle.on_key_release(key)
