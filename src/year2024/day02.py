# Problem statement: https://adventofcode.com/2024/day/2

from collections import Counter, defaultdict, deque
from typing import List, Iterator

day_title = "Red-Nosed Reports"

MAX_DELTA = 3


def parse_input(text_input: str) -> List[List[int]]:
    lines = text_input.split("\n")
    reports = [[int(i) for i in line.split()] for line in lines]
    return reports


def is_safe(report: List[int]) -> bool:
    all_increasing = all(a < b for a, b in zip(report[:-1], report[1:]))
    all_decreasing = all(a > b for a, b in zip(report[:-1], report[1:]))
    max_delta = max(abs(a - b) for a, b in zip(report[:-1], report[1:]))
    return (all_increasing or all_decreasing) and max_delta <= MAX_DELTA


def part1(text_input: str) -> int:
    reports = parse_input(text_input)
    answer = sum(is_safe(report) for report in reports)
    return answer


def remove_level(report: List[int]) -> Iterator[List[int]]:
    for k in range(len(report)):
        yield [value for i, value in enumerate(report) if i != k]


def is_safe2(report: List[int]) -> bool:
    return any(is_safe(r) for r in remove_level(report))


def part2(text_input: str) -> int:
    reports = parse_input(text_input)
    print(text_input)
    answer = sum(is_safe2(report) for report in reports)
    return answer


test_input = """
7 6 4 2 1
1 2 7 8 9
9 7 6 2 1
1 3 2 4 5
8 6 4 4 1
1 3 6 7 9
""".strip()


def test_parse_input():
    reports = parse_input(test_input)
    assert reports[0] == [7, 6, 4, 2, 1]
    assert reports[1] == [1, 2, 7, 8, 9]


def test_part1():
    assert part1(test_input) == 2


def test_is_safe2():
    assert is_safe2([7, 6, 4, 2, 1])
    assert not is_safe2([1, 2, 7, 8, 9])
    assert not is_safe2([9, 7, 6, 2, 1])
    assert is_safe2([1, 3, 2, 4, 5])


def test_part2():
    assert part2(test_input) == 4
