# Problem statement: https://adventofcode.com/2024/day/19

from functools import cache

day_title = "Linen Layout"


def parse_input(text_input: str):
    towels, designs = text_input.split("\n\n")
    towels = towels.split(", ")
    designs = designs.split()
    return towels, designs


def part1(text_input: str) -> int:
    towels, designs = parse_input(text_input)
    total = 0

    @cache
    def can_make_design(design):
        for towel in towels:
            if towel == design:
                return True
            elif towel == design[: len(towel)]:
                can_do = can_make_design(design[len(towel) :])
                if can_do:
                    return True
        return False

    for design in designs:
        total += can_make_design(design)
    return total


def part2(text_input: str) -> int:
    towels, designs = parse_input(text_input)
    total = 0

    @cache
    def count_ways_to_make_design(design):
        total = 0
        for towel in towels:
            if towel == design:
                total += 1
            elif towel == design[: len(towel)]:
                total += count_ways_to_make_design(design[len(towel) :])
        return total

    for design in designs:
        total += count_ways_to_make_design(design)
    return total


test_input = """
r, wr, b, g, bwu, rb, gb, br

brwrr
bggr
gbbr
rrbgbr
ubwu
bwurrg
brgr
bbrgwb
""".strip()


def test_part1():
    assert part1(test_input) == 6


def test_part2():
    assert part2(test_input) == 16
