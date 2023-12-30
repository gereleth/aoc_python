# Problem statement: https://adventofcode.com/2023/day/16

from functools import cache
from util.inputs import movechars_dr_dc

day_title = "The Floor Will Be Lava"

example_input = r"""
.|...\....
|.-.\.....
.....|-...
........|.
..........
.........\
..../.\\..
.-.-/..|..
.|....-|.\
..//.|....
""".strip()


direction_transforms = {
    "\\": {">": "v", "v": ">", "<": "^", "^": "<"},
    "/": {">": "^", "v": "<", "<": "v", "^": ">"},
    ".": {">": ">", "v": "v", "<": "<", "^": "^"},
    "|": {">": "^v", "v": "v", "<": "^v", "^": "^"},
    "-": {">": ">", "v": "<>", "<": "<", "^": "<>"},
}


class MirrorsCave:
    def __init__(self, text):
        self.lines = text.split("\n")
        self.R = len(self.lines)
        self.C = len(self.lines[0])

    @cache
    def process_beam(self, origin):
        r, c, direction = origin
        energized = set()
        dr, dc = movechars_dr_dc[direction]
        newdirs = ""
        while True:
            energized.add((r, c))
            r += dr
            c += dc
            if r < 0 or r >= self.R or c < 0 or c >= self.C:
                break
            newchar = self.lines[r][c]
            if newchar != ".":
                newdirs = direction_transforms[newchar][direction]
                break
        new_origins = [(r, c, newdir) for newdir in newdirs]
        return energized, new_origins

    def count_energized_tiles(self, origin):
        processed = set()
        origins = set((origin,))
        energized = set()
        while len(origins) > 0:
            origin = origins.pop()
            processed.add(origin)
            new_energized, new_origins = self.process_beam(origin)
            energized.update(new_energized)
            origins.update(o for o in new_origins if o not in processed)
        return len(energized) - 1

    def iter_origins(self):
        for r in range(0, self.R):
            yield (r, -1, ">")
        for c in range(0, self.C):
            yield (self.R, c, "^")
        for r in range(self.R, -1, -1):
            yield (r, self.C, "<")
        for c in range(self.C, -1, -1):
            yield (-1, c, "v")


def part1(text_input):
    cave = MirrorsCave(text_input)
    origin = next(cave.iter_origins())
    energized = cave.count_energized_tiles(origin)
    return energized


def part2(text_input):
    cave = MirrorsCave(text_input)
    best = 0
    for origin in cave.iter_origins():
        cnt = cave.count_energized_tiles(origin)
        best = max(best, cnt)
    return best


def test_part1():
    assert part1(example_input) == 46


def test_part2():
    assert part2(example_input) == 51
