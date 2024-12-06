# Problem statement: https://adventofcode.com/2024/day/6

from collections import defaultdict
from functools import cache


day_title = "Guard Gallivant"


class GuardGallivant:
    DIRECTIONS = [(-1, 0), (0, 1), (1, 0), (0, -1)]

    def __init__(self, text: str):
        idx = text.index("^")
        lines = text.split("\n")
        self.R = len(lines)
        self.C = len(lines[0])
        self.r0 = idx // (self.C + 1)
        self.c0 = idx % (self.C + 1)
        self.direction = 0
        self.obstruction = None

        self.row_walls = defaultdict(list)
        self.col_walls = defaultdict(list)
        for r in range(self.R):
            for c in range(self.C):
                if lines[r][c] != "#":
                    continue
                self.row_walls[r].append(c)
                self.col_walls[c].append(r)

    @cache
    def next_wall(self, r0, c0, d):
        """
        Find next wall or field edge going from (r0, c0) in direction d
        Returns (wall_r, wall_c)
        """
        dr, dc = self.DIRECTIONS[d]
        if dr == 1:
            # moving down
            wr, wc = (
                next(iter(r for r in self.col_walls[c0] if r > r0), self.R),
                self.c0,
            )
        elif dr == -1:
            # moving up
            wr, wc = (
                next(iter(r for r in self.col_walls[c0][::-1] if r < r0), -1),
                self.c0,
            )
        elif dc == 1:
            wr, wc = (
                self.r0,
                next(iter(c for c in self.row_walls[r0] if c > c0), self.C),
            )
        elif dc == -1:
            wr, wc = (
                self.r0,
                next(iter(c for c in self.row_walls[r0][::-1] if c < c0), -1),
            )
        return wr, wc

    def walk(self):
        """
        Guard walks to next wall (or edge) and makes a turn
        returns (r0, c0, r, c, direction, finished)
        where (r0, c0) - starting point
        (r, c) - ending point
        direction - new direction
        finished - True if reached the edge
        """
        wr, wc = self.next_wall(self.r0, self.c0, self.direction)
        if self.obstruction:
            obsr, obsc = self.obstruction
            if (
                obsr <= max(wr, self.r0)
                and obsc <= max(wc, self.c0)
                and obsr >= min(wr, self.r0)
                and obsc >= min(wc, self.c0)
            ):
                # we hit an obstruction instead of reaching that wall
                wr, wc = obsr, obsc
        dr, dc = self.DIRECTIONS[self.direction]
        r = wr - dr
        c = wc - dc

        finished = wr < 0 or wr >= self.R or wc < 0 or wc >= self.C
        self.direction = (self.direction + 1) % 4
        result = (self.r0, self.c0, r, c, self.direction, finished)
        self.r0 = r
        self.c0 = c
        return result


def collect_visited(guard: GuardGallivant):
    initial = (guard.r0, guard.c0, guard.direction)
    visited = set()
    while True:
        r0, c0, r, c, _, finished = guard.walk()
        r1, r2 = (r0, r) if r0 <= r else (r, r0)
        c1, c2 = (c0, c) if c0 <= c else (c, c0)
        visited.update(
            (row, col) for row in range(r1, r2 + 1) for col in range(c1, c2 + 1)
        )
        if finished:
            break
    (guard.r0, guard.c0, guard.direction) = initial
    return visited


def part1(text_input: str) -> int:
    guard = GuardGallivant(text_input)
    visited = collect_visited(guard)
    return len(visited)


def part2(text_input: str) -> int:
    guard = GuardGallivant(text_input)
    r0, c0 = guard.r0, guard.c0
    visited = collect_visited(guard)
    visited.remove((r0, c0))
    loops = 0
    for obstruction in visited:
        guard.r0, guard.c0, guard.direction = r0, c0, 0
        guard.obstruction = obstruction
        seen = set()
        while True:
            _, _, r, c, direction, finished = guard.walk()
            if finished:
                break
            state = (r, c, direction)
            if state in seen:
                loops += 1
                break
            seen.add(state)
    return loops


test_input = """
....#.....
.........#
..........
..#.......
.......#..
..........
.#..^.....
........#.
#.........
......#...
""".strip()

test_input_2 = """

""".strip()


def test_part1():
    assert part1(test_input) == 41


def test_part2():
    assert part2(test_input) == 6
