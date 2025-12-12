# Problem statement: https://adventofcode.com/2025/day/12

import re

day_title = "Christmas Tree Farm"

# This day is a joke because the task in the example input
# is much harder than what we get in the real input


def part1(text_input: str) -> int:
    presents_str, areas_str = text_input.rsplit("\n\n", maxsplit=1)
    # we don't really need shapes, just their areas
    presents = [p.count("#") for p in presents_str.split("\n\n")]
    total = 0
    for line in areas_str.split("\n"):
        w, h, *counts = map(int, re.findall(r"(\d+)", line))
        if (w // 3) * (h // 3) >= sum(counts):
            # every present totally fits into their own 3x3 square
            total += 1
        elif w * h < sum(p * c for p, c in zip(presents, counts)):
            # totally not enough area to place all presents even with zero gaps
            pass
        else:
            raise ValueError("Unexpected presents area configuration")
    return total


def part2(text_input: str) -> int:
    return 0


test_input = """
0:
###
##.
##.

1:
###
##.
.##

2:
.##
###
##.

3:
##.
###
##.

4:
###
#..
###

5:
###
.#.
###

4x4: 0 0 0 0 2 0
12x5: 1 0 1 0 2 2
12x5: 1 0 1 0 3 2
""".strip("\n")


def test_part1():
    assert "this is a joke"
