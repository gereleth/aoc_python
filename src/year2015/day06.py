# Problem statement: https://adventofcode.com/2015/day/6

import numpy as np
import re

day_title = "Probably a Fire Hazard"

instruction_regex = re.compile(
    r"(turn on|toggle|turn off) (\d+),(\d+) through (\d+),(\d+)"
)


def part1(text_input):
    lights = np.zeros((1000, 1000), dtype=bool)
    for line in text_input.split("\n"):
        action, start1, start2, end1, end2 = re.findall(instruction_regex, line)[0]
        start1, start2, end1, end2 = (
            int(start1),
            int(start2),
            int(end1) + 1,
            int(end2) + 1,
        )
        if action == "turn on":
            lights[start1:end1, start2:end2] = True
        elif action == "turn off":
            lights[start1:end1, start2:end2] = False
        elif action == "toggle":
            lights[start1:end1, start2:end2] = ~lights[start1:end1, start2:end2]
        else:
            raise ValueError("Unknown action in line " + line)
    return lights.sum()


def test_part1():
    text = """
turn on 0,0 through 999,999
toggle 0,0 through 999,0
turn off 499,499 through 500,500
    """.strip()
    assert part1(text) == 1_000_000 - 1_000 - 4


def part2(text_input):
    lights = np.zeros((1000, 1000), dtype=np.int32)
    for line in text_input.split("\n"):
        action, start1, start2, end1, end2 = re.findall(instruction_regex, line)[0]
        start1, start2, end1, end2 = (
            int(start1),
            int(start2),
            int(end1) + 1,
            int(end2) + 1,
        )
        if action == "turn on":
            lights[start1:end1, start2:end2] = lights[start1:end1, start2:end2] + 1
        elif action == "turn off":
            lights[start1:end1, start2:end2] = (
                lights[start1:end1, start2:end2] - 1
            ).clip(min=0)
        elif action == "toggle":
            lights[start1:end1, start2:end2] = lights[start1:end1, start2:end2] + 2
        else:
            raise ValueError("Unknown action in line " + line)
    return lights.sum()


def test_part2():
    text = """
turn on 0,0 through 999,999
toggle 0,0 through 999,0
turn off 499,499 through 500,500
turn off 499,499 through 500,500
    """.strip()
    assert part2(text) == 1_000_000 + 2_000 - 4
