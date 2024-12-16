import argparse
import time
from aocd import get_data, submit
from datetime import datetime as dt
from importlib import import_module


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [-y {year}] [-d {day}] [--input {filepath}]",
        description="Solve Advent Of Code puzzles.",
    )
    parser.add_argument(
        "-y",
        "--year",
        type=int,
    )
    parser.add_argument(
        "-d",
        "--day",
        type=int,
    )
    parser.add_argument(
        "-s",
        "--submit",
        type=int,
    )
    parser.add_argument("-i", "--input", type=str, help="filepath for input file")
    return parser


def run_day(year, day, input_path=None, submit_answer=0):
    try:
        solution = import_module(f"year{year}.day{day:02d}")
    except ModuleNotFoundError:
        return "?", (0, 0)
    print(f"--- Year {year} Day {day}: {solution.day_title} ---")
    if input_path is None:
        content = get_data(year=year, day=day, block=True)
    else:
        with open(input_path, "r") as f:
            content = f.read().rstrip()
    t0 = time.perf_counter()
    answer1 = solution.part1(content)
    t1 = time.perf_counter()
    print(f"Part 1: {answer1} ({t1-t0:.3f} s)")
    if submit_answer == 1:
        submit(answer1, part="a", day=day, year=year)
    t2 = time.perf_counter()
    answer2 = solution.part2(content)
    t3 = time.perf_counter()
    print(f"Part 2: {answer2} ({t3-t2:.3f} s)")
    if submit_answer == 2:
        submit(answer2, part="b", day=day, year=year)
    return solution.day_title, (answer1, t1 - t0), (answer2, t3 - t2)


if __name__ == "__main__":
    parser = init_argparse()
    args = parser.parse_args()

    if args.input is not None:
        if args.day is None:
            print("Please set --year {year} and --day {day} if giving an input file")
        else:
            day_title, *ans_times = run_day(args.year, args.day, args.input)
    else:
        if args.year is not None:
            year = args.year
        else:
            year = dt.now().year
        if args.day is not None:
            days = [args.day]
        else:
            days = range(1, 26)
        time_total = 0
        for day in days:
            day_title, *ans_times = run_day(
                year, day, input_path=args.input, submit_answer=args.submit
            )
            time_total += sum(at[1] for at in ans_times)
        print(f"Total time: {time_total:.3f}s")
