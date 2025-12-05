# Problem statement: https://adventofcode.com/2025/day/4

from typing import Set

day_title = "Printing Department"


def parse_input(text_input: str) -> Set[tuple[int, int]]:
    lines = text_input.split()
    grid = set()
    for r, line in enumerate(lines):
        for c, char in enumerate(line):
            if char == "@":
                grid.add((r, c))
    return grid


neighbourhood = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def part1(text_input: str) -> int:
    grid = parse_input(text_input)
    total = 0
    for r, c in grid:
        nearby = 0
        for dr, dc in neighbourhood:
            if (r + dr, c + dc) in grid:
                nearby += 1
        if nearby < 4:
            total += 1
    return total


def part2(text_input: str) -> int:
    grid = parse_input(text_input)
    total = 0
    remove = set((None,))  # dummy to enter the loop
    while remove:
        remove.clear()
        for r, c in grid:
            nearby = 0
            for dr, dc in neighbourhood:
                if (r + dr, c + dc) in grid:
                    nearby += 1
            if nearby < 4:
                remove.add((r, c))
        total += len(remove)
        grid.difference_update(remove)
    return total


test_input = """
..@@.@@@@.
@@@.@.@.@@
@@@@@.@.@@
@.@@@@..@.
@@.@@@@.@@
.@@@@@@@.@
.@.@.@.@@@
@.@@@.@@@@
.@@@@@@@@.
@.@.@@@.@.
""".strip()


def test_part1():
    assert part1(test_input) == 13


def test_part2():
    assert part2(test_input) == 43
