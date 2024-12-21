# Problem statement: https://adventofcode.com/2024/day/20

from collections import Counter
from typing import Iterator

day_title = "Race Condition"


class RaceConditionMaze:
    DIRECTIONS = [(1, 0), (0, 1), (-1, 0), (0, -1)]

    def __init__(self, text: str):
        self.lines = text.split("\n")
        self.R, self.C = len(self.lines), len(self.lines[0])
        start = text.index("S")
        self.start = (start // (self.C + 1), start % (self.C + 1))
        finish = text.index("E")
        self.finish = (finish // (self.C + 1), finish % (self.C + 1))
        self.distance_from_start = self.collect_distance()
        self.no_cheat_cost = self.distance_from_start[self.finish]

    def iter_neighbours(self, point: tuple[int, int]) -> Iterator[tuple[int, int]]:
        r0, c0 = point
        for dr, dc in self.DIRECTIONS:
            r, c = r0 + dr, c0 + dc
            if r >= self.R or r < 0 or c >= self.C or c < 0 or self.lines[r][c] == "#":
                continue
            yield (r, c)

    # Used to be Dijkstra but since the maze has no junctions...
    # Just follow the corridor...
    def collect_distance(self):
        distance = {}
        point = self.start
        destination = self.finish
        distance[point] = 0
        cost = 0
        while point != destination:
            for neighbour in self.iter_neighbours(point):
                if neighbour not in distance:
                    cost += 1
                    distance[neighbour] = cost
                    point = neighbour
                    break
        return distance

    def cheat_gains(self, cheat_steps=2, min_gain=1):
        for (r0, c0), dist_start in self.distance_from_start.items():
            rmin = max(0, r0 - cheat_steps)
            rmax = min(self.R, r0 + cheat_steps + 1)
            for r in range(rmin, rmax):
                dr = abs(r - r0)
                csteps = cheat_steps - dr
                cmin = max(0, c0 - csteps)
                cmax = min(self.C, c0 + 1 + csteps)
                for c in range(cmin, cmax):
                    pos = (r, c)
                    d = self.distance_from_start.get(pos, -1)
                    if d < dist_start:
                        continue
                    gain = d - dist_start - dr - abs(c0 - c)
                    if gain >= min_gain:
                        yield gain, (r0, c0), pos


def part1(text_input: str) -> int:
    maze = RaceConditionMaze(text_input)
    ans = sum(1 for _ in maze.cheat_gains(cheat_steps=2, min_gain=100))
    return ans


def part2(text_input: str) -> int:
    maze = RaceConditionMaze(text_input)
    ans = sum(1 for _ in maze.cheat_gains(cheat_steps=20, min_gain=100))
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
    cheats = Counter(maze.cheat_gains(cheat_steps=2, min_gain=1))
    assert cheats[2] == 14
    assert cheats[4] == 14
    assert cheats[6] == 2
    assert cheats[8] == 4
    assert cheats[10] == 2
    assert cheats[12] == 3
    assert cheats[20] == 1
    assert cheats[36] == 1
    assert cheats[38] == 1
    assert cheats[40] == 1
    assert cheats[64] == 1
    assert len(cheats) == 11


def test_cheat_costs_20():
    maze = RaceConditionMaze(test_input)
    cheats = Counter(maze.cheat_gains(cheat_steps=20, min_gain=50))
    assert cheats[50] == 32
    assert cheats[52] == 31
    assert cheats[54] == 29
    assert cheats[56] == 39
    assert cheats[58] == 25
    assert cheats[60] == 23
    assert cheats[62] == 20
    assert cheats[64] == 19
    assert cheats[66] == 12
    assert cheats[68] == 14
    assert cheats[70] == 12
    assert cheats[72] == 22
    assert cheats[74] == 4
    assert cheats[76] == 3
    assert len(cheats) == 14
