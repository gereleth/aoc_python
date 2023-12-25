# Problem statement: https://adventofcode.com/2023/day/21

import numpy as np
from util.inputs import movechars_dr_dc

day_title = "Step Counter"

example_input = """
...........
.....###.#.
.###.##..#.
..#.#...#..
....#.#....
.##..S####.
.##..#...#.
.......##..
.##.#.####.
.##..##.##.
...........
""".strip()


class FarmWorld:
    def __init__(self, text, wrap=False):
        self.lines = text.split("\n")
        self.wrap = wrap
        start_pos = None
        for r, line in enumerate(self.lines):
            for c, char in enumerate(line):
                if char == "S":
                    start_pos = (r, c)
                    self.lines[r] = line.replace("S", ".")
                    break
            if start_pos is not None:
                break
        self.r0, self.c0 = start_pos
        self.prev_layer = set()
        self.current_layer = set((start_pos,))
        self.layer_sizes = [1]
        self.R = len(self.lines)
        self.C = len(self.lines[0])
        self.steps = 0

    def steps_from(self, r0, c0):
        if self.wrap:
            for dr, dc in movechars_dr_dc.values():
                r, c = r0 + dr, c0 + dc
                ri = (r + self.R) % self.R
                ci = (c + self.C) % self.C
                if self.lines[ri][ci] != "#":
                    yield (r, c)
        else:
            for dr, dc in movechars_dr_dc.values():
                r, c = r0 + dr, c0 + dc
                if r < 0 or r >= self.R or c < 0 or c >= self.C:
                    continue
                if self.lines[r][c] != "#":
                    yield (r, c)

    def take_step(self):
        self.steps += 1
        new_layer = set()
        for pos0 in self.current_layer:
            for pos in self.steps_from(*pos0):
                if pos not in self.prev_layer:
                    new_layer.add(pos)
        self.layer_sizes.append(len(new_layer))
        self.prev_layer = self.current_layer
        self.current_layer = new_layer

    @property
    def total(self):
        i = self.steps % 2
        return sum(size for size in self.layer_sizes[i::2])

    def total_at(self, step):
        if step + 1 <= len(self.layer_sizes):
            i = step % 2
            return sum(size for size in self.layer_sizes[i : step + 2 : 2])
        else:
            raise ValueError("Not enough steps done")


def count_1(text_input, steps):
    world = FarmWorld(text_input, wrap=False)
    for _ in range(steps):
        world.take_step()
    return world.total


def test_part1():
    assert count_1(example_input, 6) == 16


def part1(text_input: str):
    return count_1(text_input, 64)


# This only works due to rhombic nature of input data
# I couldn't get a method of this type to work on example input
# But doing the necessary amount of steps one by one is impossible
def count_2(text_input, steps):
    world = FarmWorld(text_input, wrap=True)
    offset = steps % world.R
    while True:
        world.take_step()
        if world.steps == steps:
            return world.total
        if (world.steps % world.R == offset) and (
            (world.steps - offset) // world.R >= 2
        ):
            n0 = world.total_at(world.steps - 2 * world.R)
            n1 = world.total_at(world.steps - 1 * world.R)
            n2 = world.total
            a, b, c = np.polyfit([0, 1, 2], [n0, n1, n2], deg=2)
            a, b, c = round(a), round(b), round(c)
            n = steps // world.R
            return a * n * n + b * n + c


def part2(text_input: str):
    return count_2(text_input, 26501365)
