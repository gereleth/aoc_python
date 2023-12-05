import argparse
import time
from aocd import get_data, submit
from datetime import datetime as dt
from importlib import import_module


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [-y {year}] [-d {day}] [--input {filepath}]",
        description="Visualize Advent Of Code puzzles.",
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
    return parser


def run_day(year, day, input_path=None, submit_answer=0):
    try:
        vis = import_module(f"year{year}.day{day:02d}vis")
        vis.run()
    except ModuleNotFoundError as e:
        print(e)
        print("No vis found for year {year} day {day}")


if __name__ == "__main__":
    parser = init_argparse()
    args = parser.parse_args()

    if args.year is not None:
        year = args.year
    else:
        year = dt.now().year
    if args.day is not None:
        days = [args.day]
    else:
        days = [dt.now().day]
    for day in days:
        run_day(year, day)
