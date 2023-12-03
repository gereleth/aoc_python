# Problem statement: https://adventofcode.com/2023/day/2
# This feels so clumsy but hey it works.

import re
from collections import defaultdict

day_title = "Gear Ratios"

example_input = """
467..114..
...*......
..35..633.
......#...
617*......
.....+.58.
..592.....
......755.
...$.*....
.664.598..
""".strip()


def part1(text_input):
    total = 0
    lines = text_input.split("\n")
    for i, line in enumerate(lines):
        start_line = max(i - 1, 0)
        end_line = min(i + 2, len(lines))
        for match in re.finditer(r"(\d+)", line):
            start_check = max(0, match.start() - 1)
            end_check = min(len(line), match.end() + 1)
            check_symbols = "".join(
                lines[l][start_check:end_check] for l in range(start_line, end_line)
            )
            is_part_number = any(
                not char.isnumeric() and char != "." for char in check_symbols
            )
            if is_part_number:
                total += int(match.group())
    return total


def test_part_1():
    assert part1(example_input) == 4361


def part2(text_input):
    total = 0
    lines = text_input.split("\n")
    potential_gears = defaultdict(list)
    for i, line in enumerate(lines):
        start_line = max(i - 1, 0)
        end_line = min(i + 2, len(lines))
        for match in re.finditer(r"(\d+)", line):
            start_check = max(0, match.start() - 1)
            end_check = min(len(line), match.end() + 1)
            for l in range(start_line, end_line):
                for c in range(start_check, end_check):
                    if lines[l][c] == "*":
                        potential_gears[(l, c)].append(int(match.group()))
    for numbers in potential_gears.values():
        if len(numbers) == 2:
            total += numbers[0] * numbers[1]
    return total


def test_part_2():
    assert part2(example_input) == 467835
