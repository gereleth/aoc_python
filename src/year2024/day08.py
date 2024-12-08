# Problem statement: https://adventofcode.com/2024/day/8

from collections import defaultdict

day_title = "Resonant Collinearity"


class AntennaField:
    def __init__(self, text):
        lines = text.split("\n")
        self.R, self.C = len(lines), len(lines[0])
        self.antennas = defaultdict(list)
        for r, line in enumerate(lines):
            for c, char in enumerate(line):
                if char != ".":
                    self.antennas[char].append((r, c))

    def in_range(self, r: int, c: int) -> bool:
        if r < 0 or c < 0 or r >= self.R or c >= self.C:
            return False
        return True

    def find_antinodes(self, locations, single=True):
        antinodes = set()
        for ra, ca in locations:
            if not single:
                antinodes.add((ra, ca))
            for rb, cb in locations:
                if (ra, ca) == (rb, cb):
                    continue
                dr, dc = rb - ra, cb - ca
                rn, cn = ra - dr, ca - dc
                while self.in_range(rn, cn):
                    antinodes.add((rn, cn))
                    rn, cn = rn - dr, cn - dc
                    if single:
                        break
        return antinodes

    def find_all_antinodes(self, single=True):
        nodes = set()
        for _, locations in self.antennas.items():
            nodes.update(self.find_antinodes(locations, single=single))
        return nodes


def part1(text_input: str) -> int:
    antenna_field = AntennaField(text_input)
    antinodes = antenna_field.find_all_antinodes(single=True)
    return len(antinodes)


def part2(text_input: str) -> int:
    antenna_field = AntennaField(text_input)
    antinodes = antenna_field.find_all_antinodes(single=False)
    return len(antinodes)


test_input = """
............
........0...
.....0......
.......0....
....0.......
......A.....
............
............
........A...
.........A..
............
............
""".strip()

test_input_2 = """

""".strip()


def test_part1():
    assert part1(test_input) == 14


def test_part2():
    assert part2(test_input) == 34
