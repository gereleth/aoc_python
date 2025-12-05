# Problem statement: https://adventofcode.com/2025/day/1

from typing import List
import random

day_title = "Secret Entrance"


def parse_input(text_input: str) -> List[int]:
    rotations = text_input.split()
    numeric_rotations = [int(r[1:]) * (1 if r[0] == "R" else -1) for r in rotations]
    return numeric_rotations


def part1(text_input: str) -> int:
    pos = 50
    point_at_zero_times = 0
    for rotation in parse_input(text_input):
        pos += rotation
        point_at_zero_times += (pos % 100) == 0
    return point_at_zero_times


def part2(text_input: str) -> int:
    pos = 50
    point_at_zero_times = 0
    for rotation in parse_input(text_input):
        if rotation < 0:
            point_at_zero_times += -(pos % 100 == 0) + ((pos + rotation) % 100 == 0)
        point_at_zero_times += abs((pos + rotation) // 100 - pos // 100)
        pos += rotation
    return point_at_zero_times


def dumb_part2(text_input: str) -> int:
    pos = 50
    point_at_zero_times = 0
    for rotation in parse_input(text_input):
        delta = -1 if rotation < 0 else 1
        for _ in range(abs(rotation)):
            pos += delta
            pos %= 100
            point_at_zero_times += pos == 0
    return point_at_zero_times


test_input = """
L68
L30
R48
L5
R60
L55
L1
L99
R14
L82
""".strip()


def test_part1():
    assert part1(test_input) == 3


def test_part2():
    assert dumb_part2(test_input) == 6
    assert part2(test_input) == 6


def test_part2_edge_cases():
    assert part2("R240") == 2
    assert part2("R250") == 3
    assert part2("R50 R240") == 3
    assert part2("R50 R250") == 3
    assert part2("R50 L10") == 1
    assert part2("R50 L100") == 2
    assert part2("R50 L110") == 2
    assert part2("R50 L150") == 2
    assert part2("L10") == 0
    assert part2("L50") == 1
    assert part2("L150") == 2
    assert part2("L160") == 2
