# Problem statement: https://adventofcode.com/2023/day/14

day_title = "Parabolic Reflector Dish"

example_input = """
O....#....
O.OO#....#
.....##...
OO.#O....O
.O.....O#.
O.#..O.#.#
..O..#O..O
.......O..
#....###..
#OO..#....
""".strip()


class TiltPlatform:
    def __init__(self, text):
        self.lines = [list(line) for line in text.split("\n")]
        self.R = len(self.lines)
        self.C = len(self.lines[0])

    def calc_load(self):
        total = 0
        for r, line in enumerate(self.lines):
            total += line.count("O") * (self.R - r)
        return total

    def roll_north(self):
        for col in range(self.C):
            rounds = 0
            for row in range(self.R - 1, -1, -1):
                if self.lines[row][col] == "O":
                    rounds += 1
                    self.lines[row][col] = "."
                elif self.lines[row][col] == "#":
                    for r in range(rounds):
                        self.lines[row + r + 1][col] = "O"
                    rounds = 0
            for r in range(rounds):
                self.lines[r][col] = "O"
        return self

    def roll_south(self):
        for col in range(self.C):
            rounds = 0
            for row in range(self.R):
                if self.lines[row][col] == "O":
                    rounds += 1
                    self.lines[row][col] = "."
                elif self.lines[row][col] == "#":
                    for r in range(rounds):
                        self.lines[row - r - 1][col] = "O"
                    rounds = 0
            for r in range(rounds):
                self.lines[self.R - 1 - r][col] = "O"
        return self

    def roll_east(self):
        for row in range(self.R):
            rounds = 0
            for col in range(self.C):
                if self.lines[row][col] == "O":
                    rounds += 1
                    self.lines[row][col] = "."
                elif self.lines[row][col] == "#":
                    for r in range(rounds):
                        self.lines[row][col - r - 1] = "O"
                    rounds = 0
            for r in range(rounds):
                self.lines[row][self.C - r - 1] = "O"
        return self

    def roll_west(self):
        for row in range(self.R):
            rounds = 0
            for col in range(self.C - 1, -1, -1):
                if self.lines[row][col] == "O":
                    rounds += 1
                    self.lines[row][col] = "."
                elif self.lines[row][col] == "#":
                    for r in range(rounds):
                        self.lines[row][col + r + 1] = "O"
                    rounds = 0
            for r in range(rounds):
                self.lines[row][r] = "O"
        return self

    def spin_cycle(self):
        return self.roll_north().roll_west().roll_south().roll_east()

    def gist(self):
        return "\n".join("".join(line) for line in self.lines)


def part1(text_input):
    platform = TiltPlatform(text_input)
    platform.roll_north()
    return platform.calc_load()


def part2(text_input):
    platform = TiltPlatform(text_input)
    last_seen = {}
    period = 0
    want = 1_000_000_000
    for cycle in range(want):
        gist = platform.spin_cycle().gist()
        if gist in last_seen:
            period = cycle - last_seen[gist]
            break
        else:
            last_seen[gist] = cycle
    todo = (want - cycle) % period - 1
    for cycle in range(todo):
        platform.spin_cycle()
    return platform.calc_load()


def test_part1():
    assert part1(example_input) == 136


def test_part2():
    assert part2(example_input) == 64
