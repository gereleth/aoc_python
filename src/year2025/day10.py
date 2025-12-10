# Problem statement: https://adventofcode.com/2025/day/10

import re
from collections import deque
from scipy.optimize import linprog
import numpy as np

day_title = "Factory"


def parse_machine(line: str):
    lights, rest = line.split(maxsplit=1)
    buttons, joltages = rest.rsplit(maxsplit=1)
    lights = tuple(char == "#" for char in lights[1:-1])
    buttons = [
        set(int(i) for i in re.findall(r"\d+", button)) for button in buttons.split()
    ]
    joltages = tuple(int(i) for i in re.findall(r"\d+", joltages))
    return lights, buttons, joltages


def configure_lights(lights: tuple[int], buttons: list[set[int]]):
    initial = tuple(0 for _ in lights)
    states = deque([(0, initial)])
    seen = {(initial,)}
    while states:
        count, current = states.popleft()
        for button in buttons:
            after = tuple(
                not light if i in button else light for i, light in enumerate(current)
            )
            if after == lights:
                return count + 1
            elif after not in seen:
                states.append((count + 1, after))
                seen.add(after)
    return -1


def configure_joltages(buttons: list[set[int]], joltages: tuple[int]):
    c = [1 for _ in buttons]
    A_eq = np.zeros((len(joltages), len(buttons)))
    for b, button in enumerate(buttons):
        A_eq[list(button), b] = 1
    res = linprog(c, A_eq=A_eq, b_eq=joltages, integrality=1)
    return int(res.x.sum())


def part1(text_input: str) -> int:
    total = 0
    for line in text_input.split("\n"):
        lights, buttons, _ = parse_machine(line)
        total += configure_lights(lights, buttons)
    return total


def part2(text_input: str) -> int:
    total = 0
    for line in text_input.split("\n"):
        _, buttons, joltages = parse_machine(line)
        total += configure_joltages(buttons, joltages)
    return total


test_input = """
[.##.] (3) (1,3) (2) (2,3) (0,2) (0,1) {3,5,4,7}
[...#.] (0,2,3,4) (2,3) (0,4) (0,1,2) (1,2,3,4) {7,5,12,7,2}
[.###.#] (0,1,2,3,4) (0,3,4) (0,1,2,4,5) (1,2) {10,11,11,5,10,5}
""".strip("\n")


def test_part1():
    totals = [2, 3, 2]
    for line, total in zip(test_input.split("\n"), totals):
        lights, buttons, _ = parse_machine(line)
        assert configure_lights(lights, buttons) == total


def test_part2():
    totals = [10, 12, 11]
    for line, total in zip(test_input.split("\n"), totals):
        _, buttons, joltages = parse_machine(line)
        assert configure_joltages(buttons, joltages) == total
