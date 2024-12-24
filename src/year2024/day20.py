# Problem statement: https://adventofcode.com/2024/day/20

from typing import Iterator
import numpy as np

day_title = "Race Condition"


class RaceConditionMaze:
    DIRECTIONS = [(1, 0), (0, 1), (-1, 0), (0, -1)]

    def __init__(self, text: str):
        self.lines = text.split("\n")
        self.R, self.C = len(self.lines), len(self.lines[0])
        # floats because nans are convenient for walls
        self.distance = np.nan + np.zeros(shape=(self.R, self.C), dtype=np.float32)
        start = text.index("S")
        self.start = (start // (self.C + 1), start % (self.C + 1))
        finish = text.index("E")
        self.finish = (finish // (self.C + 1), finish % (self.C + 1))
        self.collect_distance()
        self.no_cheat_cost = int(self.distance[self.finish[0], self.finish[1]])

    def iter_neighbours(self, point: tuple[int, int]) -> Iterator[tuple[int, int]]:
        r0, c0 = point
        for dr, dc in self.DIRECTIONS:
            r, c = r0 + dr, c0 + dc
            if r >= self.R or r < 0 or c >= self.C or c < 0 or self.lines[r][c] == "#":
                continue
            yield (r, c)

    # Used to be Dijkstra but since the maze has no junctions...
    # Just follow the corridor.
    def collect_distance(self):
        r0, c0 = self.start
        destination = self.finish
        self.distance[r0, c0] = 0.0
        cost = 0.0
        while (r0, c0) != destination:
            for r, c in self.iter_neighbours((r0, c0)):
                if np.isnan(self.distance[r, c]):
                    cost += 1.0
                    self.distance[r, c] = cost
                    r0, c0 = r, c
                    break

    def cheat_gains(self, cheat_steps=2, min_gain=1):
        total = 0
        for dr in range(-cheat_steps, cheat_steps + 1):
            csteps = cheat_steps - abs(dr)
            for dc in range(-csteps, csteps + 1):
                cost = abs(dr) + abs(dc)
                if cost < 2:
                    continue
                r_index_old = slice(max(0, dr), self.R + min(0, dr))
                c_index_old = slice(max(0, dc), self.C + min(0, dc))
                r_index_new = slice(max(0, -dr), self.R - max(0, dr))
                c_index_new = slice(max(0, -dc), self.C - max(0, dc))
                total += (
                    (
                        self.distance[r_index_new, c_index_new]
                        - self.distance[r_index_old, c_index_old]
                        - cost
                    )
                    >= min_gain
                ).sum()
        return total


def part1(text_input: str) -> int:
    maze = RaceConditionMaze(text_input)
    ans = maze.cheat_gains(cheat_steps=2, min_gain=100)
    # ans = sum(1 for _ in maze.cheat_gains(cheat_steps=2, min_gain=100))
    return ans


def part2(text_input: str) -> int:
    maze = RaceConditionMaze(text_input)
    ans = maze.cheat_gains(cheat_steps=20, min_gain=100)
    # ans = sum(1 for _ in maze.cheat_gains(cheat_steps=20, min_gain=100))
    return ans


test_input = """
###############
#...#...#.....#
#.#.#.#.#.###.#
#S#...#.#.#...#
#######.#.#.###
#######.#.#...#
#######.#.###.#
###..E#...#...#
###.#######.###
#...###...#...#
#.#####.#.###.#
#.#...#.#.#...#
#.#.#.#.#.#.###
#...#...#...###
###############
""".strip()


def test_no_cheat_cost():
    maze = RaceConditionMaze(test_input)
    assert maze.no_cheat_cost == 84


def test_cheat_costs_2():
    maze = RaceConditionMaze(test_input)
    assert maze.cheat_gains(cheat_steps=2, min_gain=64) == 1
    assert maze.cheat_gains(cheat_steps=2, min_gain=40) == 2
    assert maze.cheat_gains(cheat_steps=2, min_gain=38) == 3
    assert maze.cheat_gains(cheat_steps=2, min_gain=36) == 4
    assert maze.cheat_gains(cheat_steps=2, min_gain=20) == 5
    assert maze.cheat_gains(cheat_steps=2, min_gain=12) == 8
    assert maze.cheat_gains(cheat_steps=2, min_gain=10) == 10
    assert maze.cheat_gains(cheat_steps=2, min_gain=8) == 14
    assert maze.cheat_gains(cheat_steps=2, min_gain=6) == 16
    assert maze.cheat_gains(cheat_steps=2, min_gain=4) == 30
    assert maze.cheat_gains(cheat_steps=2, min_gain=2) == 44


def test_cheat_costs_20():
    maze = RaceConditionMaze(test_input)
    assert maze.cheat_gains(cheat_steps=15, min_gain=76) == 3
    assert maze.cheat_gains(cheat_steps=15, min_gain=74) == 7
    assert maze.cheat_gains(cheat_steps=15, min_gain=72) == 29
    assert maze.cheat_gains(cheat_steps=15, min_gain=70) == 41
    assert maze.cheat_gains(cheat_steps=15, min_gain=68) == 55
    assert maze.cheat_gains(cheat_steps=15, min_gain=66) == 67
    assert maze.cheat_gains(cheat_steps=15, min_gain=64) == 86
    assert maze.cheat_gains(cheat_steps=15, min_gain=62) == 106
    assert maze.cheat_gains(cheat_steps=15, min_gain=60) == 129
    assert maze.cheat_gains(cheat_steps=15, min_gain=58) == 154
