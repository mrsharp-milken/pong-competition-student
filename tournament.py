"""
Run a round-robin tournament between all paddles in the paddles/ directory.

Usage:
    python tournament.py [--games N]

Options:
    --games N   number of matches per head-to-head pair (default: 2)
                Each pair plays once as left and once as right; if N > 2,
                extra games alternate sides.

Paddles named human_paddle or example_paddle are excluded automatically.
Any paddle with a TOURNAMENT = False class attribute is also excluded.

Results are printed as a leaderboard sorted by win percentage.
"""

import sys
import importlib
import itertools
from pathlib import Path
from collections import defaultdict

from engine.paddle import Paddle
from engine.simulator import PongSimulator


PADDLES_DIR = Path(__file__).parent / "paddles"
EXCLUDE_FILES = {"human_paddle", "example_paddle", "__init__"}


def discover_paddle_classes() -> list[tuple[str, type]]:
    """Return (module_name, PaddleClass) for every eligible paddle."""
    results = []
    for path in sorted(PADDLES_DIR.glob("*.py")):
        name = path.stem
        if name.startswith("_") or name in EXCLUDE_FILES:
            continue
        module = importlib.import_module(f"paddles.{name}")
        for obj in vars(module).values():
            if (
                isinstance(obj, type)
                and issubclass(obj, Paddle)
                and obj is not Paddle
                and obj.__module__ == module.__name__
                and getattr(obj, "TOURNAMENT", True)
            ):
                results.append((name, obj))
                break  # one class per file
    return results


def run_match(left_class: type, right_class: type) -> tuple[int, int]:
    """Simulate one match and return (left_score, right_score)."""
    sim = PongSimulator(left_class, right_class)
    return sim.run()


def main() -> None:
    games_per_pair = 2
    args = sys.argv[1:]
    if "--games" in args:
        idx = args.index("--games")
        try:
            games_per_pair = int(args[idx + 1])
        except (IndexError, ValueError):
            print("--games requires an integer argument")
            sys.exit(1)

    paddles = discover_paddle_classes()

    if len(paddles) < 2:
        print("Need at least 2 paddles in the paddles/ directory to run a tournament.")
        print(f"Found: {[n for n, _ in paddles] or 'none'}")
        sys.exit(1)

    print(f"\nPong Competition Tournament")
    print(f"{'─' * 50}")
    print(f"Paddles: {', '.join(n for n, _ in paddles)}")
    print(f"Games per pair: {games_per_pair}")
    print(f"Points to win each game: {PongSimulator.POINTS_TO_WIN}")
    print(f"{'─' * 50}\n")

    wins = defaultdict(int)
    losses = defaultdict(int)
    points_scored = defaultdict(int)
    points_conceded = defaultdict(int)

    pairs = list(itertools.combinations(paddles, 2))
    total_matches = len(pairs) * games_per_pair
    match_num = 0

    for (name_a, cls_a), (name_b, cls_b) in pairs:
        for game_index in range(games_per_pair):
            match_num += 1
            # Alternate sides each game
            if game_index % 2 == 0:
                left_name, left_cls = name_a, cls_a
                right_name, right_cls = name_b, cls_b
            else:
                left_name, left_cls = name_b, cls_b
                right_name, right_cls = name_a, cls_a

            print(
                f"  [{match_num:>{len(str(total_matches))}}/{total_matches}] "
                f"{left_name} vs {right_name} ... ",
                end="",
                flush=True,
            )

            try:
                ls, rs = run_match(left_cls, right_cls)
            except Exception as e:
                print(f"ERROR: {e}")
                continue

            print(f"{ls} – {rs}")

            points_scored[left_name] += ls
            points_conceded[left_name] += rs
            points_scored[right_name] += rs
            points_conceded[right_name] += ls

            if ls > rs:
                wins[left_name] += 1
                losses[right_name] += 1
            elif rs > ls:
                wins[right_name] += 1
                losses[left_name] += 1
            # draws count as neither (shouldn't happen given POINTS_TO_WIN)

    print(f"\n{'─' * 50}")
    print(f"{'LEADERBOARD':^50}")
    print(f"{'─' * 50}")

    all_names = sorted({n for n, _ in paddles})
    rows = []
    for name in all_names:
        w = wins[name]
        l = losses[name]
        total = w + l
        pct = (w / total * 100) if total > 0 else 0.0
        ps = points_scored[name]
        pc = points_conceded[name]
        rows.append((name, w, l, pct, ps, pc))

    rows.sort(key=lambda r: (-r[3], -r[1], -r[4]))  # sort by win%, then wins, then points

    header = f"{'#':<3} {'Name':<22} {'W':>4} {'L':>4} {'Win%':>6}  {'Pts+':>5} {'Pts-':>5}"
    print(header)
    print("─" * len(header))
    for rank, (name, w, l, pct, ps, pc) in enumerate(rows, 1):
        print(f"{rank:<3} {name:<22} {w:>4} {l:>4} {pct:>5.1f}%  {ps:>5} {pc:>5}")

    print(f"{'─' * 50}\n")


if __name__ == "__main__":
    main()
