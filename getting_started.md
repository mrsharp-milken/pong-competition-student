# Getting Started

## Setup

```bash
pip3 install -r requirements.txt
```

## Play the game

You can control a paddle yourself with the keyboard:

```bash
python3 main.py human example_paddle
```

**Left side:** W = up, S = down  
**Right side:** ↑ = up, ↓ = down  
**ESC** to quit

Watch what the example paddle does. Notice anything wrong with it?

---

## Your first task — build a Chaser

A **Chaser** paddle has one job: follow the ball's y position every frame.

1. Copy the template and name your file `paddles/chaser.py`
2. Rename the class to `ChaserPaddle` and set `NAME = "Chaser"`
3. Write your strategy in `tick()`

### What you have access to in `tick()`

```python
ball.x, ball.y       # where the ball is right now
self.get_y()         # your paddle's current y position
self.max_speed       # the most pixels you can move in one call
self.set_y(value)    # move your paddle to a new y position
```

`set_y()` will raise a `ValueError` if you try to move more than `self.max_speed` in a single call.

### Test it

```bash
python3 main.py human chaser        # play against your chaser
python3 main.py chaser example_paddle  # watch the two bots play
python3 main.py chaser chaser
```

A working Chaser should be able to return the ball consistently. Once it does, think about what would beat it.
