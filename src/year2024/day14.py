# Problem statement: https://adventofcode.com/2024/day/?

from typing import List, Tuple
import re
from collections import Counter

day_title = "Restroom Redoubt"


def parse_input(text_input: str) -> List[Tuple[int]]:
    """Return a list of robots as tuples (px, py, vx, vy)"""
    numbers = re.findall(r"(-?\d+)", text_input)
    robots = []
    for i in range(0, len(numbers), 4):
        px, py, vx, vy = numbers[i : i + 4]
        robots.append((int(px), int(py), int(vx), int(vy)))
    return robots


def calc_new_positions(
    robots: List[Tuple[int]], xmax: int, ymax: int, nturns: int
) -> List[Tuple[int]]:
    positions = []
    for px, py, vx, vy in robots:
        nx = (px + nturns * vx) % xmax
        ny = (py + nturns * vy) % ymax
        positions.append((nx, ny))
    return positions


def calc_safety_index(robots: List[Tuple[int]], xmax: int, ymax: int) -> int:
    halfx, halfy = xmax // 2, ymax // 2
    counts = Counter(
        (
            int(px < halfx) * 2 + int(py < halfy)
            for px, py in robots
            if px != halfx and py != halfy
        )
    )
    total = 1
    for i in range(4):
        total *= counts[i]
    return total


def part1(text_input: str) -> int:
    robots = parse_input(text_input)
    new_robots = calc_new_positions(robots, 101, 103, 100)
    res = calc_safety_index(new_robots, 101, 103)
    return res


def part2(text_input: str, xmax=101, ymax=103) -> int:
    # detect vertical and horizontal anomalies
    # in robots movement
    # those are cyclical and when the cycles meet we get an image
    robots = parse_input(text_input)
    vertical_start = None
    horizontal_start = None
    N = max(xmax, ymax) + 1
    for turns in range(1, N):
        pos = calc_new_positions(robots, xmax, ymax, turns)
        vertical = Counter(x for x, y in pos)
        horizontal = Counter(y for x, y in pos)
        if max(vertical.values()) > 25:
            vertical_start = turns
        if max(horizontal.values()) > 25:
            horizontal_start = turns
        if horizontal_start is not None and vertical_start is not None:
            break
    # horizontal cycle starts at horizontal_start and repeats every ymax turns
    # vertical cycle starts at vertical_start and repeats every xmax turns
    for x in range(vertical_start, 100000, xmax):
        double_n = x - horizontal_start
        if double_n > 0 and double_n % 2 == 0:
            n = double_n // 2
            break
    t = horizontal_start + n * ymax
    return t


test_input = """
p=0,4 v=3,-3
p=6,3 v=-1,-3
p=10,3 v=-1,2
p=2,0 v=2,-1
p=0,0 v=1,3
p=3,0 v=-2,-2
p=7,6 v=-1,-3
p=3,0 v=-1,-2
p=9,3 v=2,3
p=7,3 v=-1,2
p=2,4 v=2,-3
p=9,5 v=-3,-3
""".strip()


def test_calc_safety_index():
    assert calc_safety_index([(0, 0), (5, 0), (0, 2), (5, 2)], 5, 3) == 1
    assert calc_safety_index([(0, 0), (1, 0), (5, 0), (0, 2), (5, 2)], 5, 3) == 2
    assert calc_safety_index([(0, 0), (1, 0), (5, 0), (0, 2), (5, 2)], 51, 31) == 0


def test_part1():
    robots = parse_input(test_input)
    new_robots = calc_new_positions(robots, 11, 7, 100)
    res = calc_safety_index(new_robots, 11, 7)
    assert res == 12
