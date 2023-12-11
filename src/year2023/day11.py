# Problem statement: https://adventofcode.com/2023/day/11

day_title = "Cosmic Expansion"

example_input = """
...#......
.......#..
#.........
..........
......#...
.#........
.........#
..........
.......#..
#...#.....
""".strip()


class ExpandingUniverse:
    def __init__(self, text, expansion_factor):
        self.lines = text.split("\n")
        self.expansion_factor = expansion_factor
        # locate galaxies
        single_line = "".join(self.lines)
        idx = [i for i, char in enumerate(single_line) if char == "#"]
        C = len(self.lines[0])
        self.galaxies = [(i // C, i % C) for i in idx]
        # precalculate distances along rows
        distance = 0
        self.distance_r = []
        for r, line in enumerate(self.lines):
            if all(char != "#" for char in line):
                distance += expansion_factor
            else:
                distance += 1
            self.distance_r.append(distance)
        # precalculate distances along columns
        distance = 0
        self.distance_c = []
        for c in range(C):
            if all(line[c] != "#" for line in self.lines):
                distance += expansion_factor
            else:
                distance += 1
            self.distance_c.append(distance)

    def get_distance(self, pos_a, pos_b):
        ra, ca = pos_a
        rb, cb = pos_b
        distance_r = abs(self.distance_r[ra] - self.distance_r[rb])
        distance_c = abs(self.distance_c[ca] - self.distance_c[cb])
        return distance_c + distance_r

    def galaxy_pairs(self):
        for a, pos_a in enumerate(self.galaxies[:-1]):
            for pos_b in self.galaxies[a + 1 :]:
                yield pos_a, pos_b


def sum_distances(text_input, expansion_factor=1):
    universe = ExpandingUniverse(text_input, expansion_factor)
    total = 0
    for pos_a, pos_b in universe.galaxy_pairs():
        total += universe.get_distance(pos_a, pos_b)
    return total


def part1(text_input: str):
    total = sum_distances(text_input, expansion_factor=2)
    return total


def test_part_1():
    assert part1(example_input) == 374


def part2(text_input: str):
    total = sum_distances(text_input, expansion_factor=1_000_000)
    return total


def test_part_2():
    assert sum_distances(example_input, expansion_factor=10) == 1030
    assert sum_distances(example_input, expansion_factor=100) == 8410
