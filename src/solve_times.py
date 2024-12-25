import os
from pathlib import Path
import argparse
import time
import pandas as pd
import matplotlib
from aocd import get_data
from importlib import import_module

matplotlib.rcParams.update({"font.size": 14})


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [--rerun]",
        description="Record solve times for Advent Of Code puzzles.",
    )
    parser.add_argument(
        "-r",
        "--rerun",
        action="store_true",
        help="rerun solutions",
    )
    parser.add_argument(
        "-y",
        "--year",
        type=int,
    )
    return parser


def run_day(year, day):
    solution = import_module(f"year{year}.day{day:02d}")
    print(f"--- Year {year} Day {day}: {solution.day_title} ---")
    content = get_data(year=year, day=day, block=True)
    times1 = []
    for _ in range(5):
        t0 = time.perf_counter()
        answer1 = solution.part1(content)
        t1 = time.perf_counter()
        times1.append(t1 - t0)
    median_time_1 = sorted(times1)[len(times1) // 2]
    print(f"Part 1: {answer1} ({sorted(times1)[len(times1)//2]:.3f} s)")
    times2 = []
    for _ in range(5):
        t2 = time.perf_counter()
        answer2 = solution.part2(content)
        t3 = time.perf_counter()
        times2.append(t3 - t2)
    median_time_2 = sorted(times2)[len(times2) // 2]
    print(f"Part 2: {answer2} ({median_time_2:.3f} s)")
    return solution.day_title, (answer1, median_time_1), (answer2, median_time_2)


if __name__ == "__main__":
    parser = init_argparse()
    args = parser.parse_args()

    path = Path("outputs") / "time_stats"
    os.makedirs(path, exist_ok=True)

    if args.rerun:
        res = []
        days = range(1, 26)
        for day in days:
            try:
                day_title, *ans_times = run_day(args.year, day)
                for i, (answer, t) in enumerate(ans_times):
                    res.append(dict(day=day, title=day_title, part=i + 1, time=t))
            except ModuleNotFoundError:
                res.append(dict(day=day, title="?", part=1, time=None))
                res.append(dict(day=day, title="?", part=2, time=None))
        res = (
            pd.DataFrame(res)
            .set_index(["day", "title", "part"])["time"]
            .unstack()
            .multiply(1000)
            .add_prefix("part_")
            .add_suffix("_ms")
        )
        res.to_csv(path / f"{args.year}.csv", float_format="%.1f")
    else:
        res = pd.read_csv(path / f"{args.year}.csv").set_index(["title", "day"])

    ax = res.multiply(0.001).plot.barh()
    ax.set(
        ylabel=None,
        xlabel="time, s",
        title=f"Solution times for Advent of Code {args.year}",
    )
    ax.legend(["Part 1", "Part 2"])
    if res.max().max() > 15 * 1000:
        ax.axvline(15, ls="dashed", lw=1)
        ax.text(
            1,
            ax.get_ylim()[0] + 3,
            "> every problem has a solution\n"
            "> that completes in at most 15 seconds\n"
            "> on ten-year-old hardware",
            ha="left",
            bbox=dict(facecolor="white", edgecolor="C0", ls="dashed"),
        )
    ax.grid()
    ax.invert_yaxis()
    ax.figure.set_size_inches(9, 9)
    ax.figure.tight_layout()
    ax.figure.savefig(path / f"{args.year}.png")
    total_ms = res.part_1_ms.sum() + res.part_2_ms.sum()
    print(f"Total time: {total_ms:.0f} ms")
