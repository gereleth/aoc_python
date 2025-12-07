# Problem statement: https://adventofcode.com/2025/day/7

from collections import Counter

day_title = "Laboratories"


def part1(text_input: str) -> int:
    lines = text_input.split("\n")
    beams = set((lines[0].index("S"),))
    splits = 0
    for line in lines[1:]:
        new_beams = set()
        for i, char in enumerate(line):
            if i not in beams:
                continue
            if char == "^":
                new_beams.update((i - 1, i + 1))
                splits += 1
            elif char == ".":
                new_beams.add(i)
        beams = new_beams
    return splits


def part2(text_input: str) -> int:
    lines = text_input.split("\n")
    beams = Counter({lines[0].index("S"): 1})
    for line in lines[1:]:
        new_beams = Counter()
        for i, char in enumerate(line):
            if i not in beams:
                continue
            if char == "^":
                new_beams[i - 1] += beams[i]
                new_beams[i + 1] += beams[i]
            elif char == ".":
                new_beams[i] += beams[i]
        beams = new_beams
    return sum(beams.values())


test_input = """
.......S.......
...............
.......^.......
...............
......^.^......
...............
.....^.^.^.....
...............
....^.^...^....
...............
...^.^...^.^...
...............
..^...^.....^..
...............
.^.^.^.^.^...^.
...............
""".strip("\n")


def test_part1():
    assert part1(test_input) == 21


def test_part2():
    assert part2(test_input) == 40
