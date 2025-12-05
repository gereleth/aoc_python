# Problem statement: https://adventofcode.com/2025/day/5

from util.segments import Segment1D, Segment1DCollection

day_title = "Cafeteria"


def part1(text_input: str) -> int:
    ranges, ids = text_input.split("\n\n")
    fresh = Segment1DCollection()
    for r in ranges.split():
        a, b = r.split("-")
        fresh += Segment1D(int(a), int(b))
    return sum(int(id) in fresh for id in ids.split())


def part2(text_input: str) -> int:
    ranges, _ = text_input.split("\n\n")
    fresh = Segment1DCollection()
    for r in ranges.split():
        a, b = r.split("-")
        fresh += Segment1D(int(a), int(b))
    return len(fresh)


test_input = """
3-5
10-14
16-20
12-18

1
5
8
11
17
32
""".strip()


def test_part1():
    assert part1(test_input) == 3


def test_part2():
    assert part2(test_input) == 14
