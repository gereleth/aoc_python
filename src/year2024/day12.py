# Problem statement: https://adventofcode.com/2024/day/12

from collections import defaultdict

day_title = "Garden Groups"


class GardenRegion:
    def __init__(self, r, c, letter):
        self.r = r
        self.c = c
        self.letter = letter
        self.plots = set([(r, c)])
        self.borders = defaultdict(list)

    @property
    def area(self):
        return len(self.plots)

    @property
    def perimeter(self):
        return sum(len(b) for b in self.borders.values())

    @property
    def sides(self):
        sides = 0
        for _, ys in self.borders.items():
            ys.sort()
            sides += 1 + sum(b - a > 1 for a, b in zip(ys[:-1], ys[1:]))
        return sides


class Farm:
    DIRECTIONS = [(-1, 0), (0, 1), (1, 0), (0, -1)]

    def __init__(self, text):
        self.lines = text.split("\n")
        self.R, self.C = len(self.lines), len(self.lines[0])
        self.regions = []

    def iter_points(self):
        for r, line in enumerate(self.lines):
            for c, char in enumerate(line):
                yield r, c, char

    def iter_neighbours(self, r, c):
        for dr, dc in self.DIRECTIONS:
            if r + dr >= self.R or r + dr < 0 or c + dc >= self.C or c + dc < 0:
                yield (r + dr, c + dc, None)
                continue
            next_letter = self.lines[r + dr][c + dc]
            yield (r + dr, c + dc, next_letter)

    def collect_regions(self):
        done = set()
        for r, c, letter in self.iter_points():
            if (r, c) in done:
                continue
            region = GardenRegion(r, c, letter)
            self.regions.append(region)
            to_explore = set([(r, c)])
            while len(to_explore) > 0:
                rg, cg = to_explore.pop()
                done.add((rg, cg))
                for rn, cn, ln in self.iter_neighbours(rg, cg):
                    if (rn, cn) in region.plots:
                        continue
                    if ln != region.letter:
                        # save region's outer border locations
                        if rn == rg:
                            region.borders[("c", cg, cn - cg)].append(rg)
                        else:
                            region.borders[("r", rg, rn - rg)].append(cg)
                        continue
                    region.plots.add((rn, cn))
                    to_explore.add((rn, cn))


def part1(text_input: str) -> int:
    farm = Farm(text_input)
    farm.collect_regions()
    return sum(r.area * r.perimeter for r in farm.regions)


def part2(text_input: str) -> int:
    farm = Farm(text_input)
    farm.collect_regions()
    return sum(r.area * r.sides for r in farm.regions)


test_input = """
RRRRIICCFF
RRRRIICCCF
VVRRRCCFFF
VVRCCCJFFF
VVVVCJJCFE
VVIVCCJJEE
VVIIICJJEE
MIIIIIJJEE
MIIISIJEEE
MMMISSJEEE
""".strip()

test_input_2 = """

""".strip()


def test_part1():
    assert part1(test_input) == 1930


def test_part2():
    assert part2(test_input) == 1206
