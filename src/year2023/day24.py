# Problem statement: https://adventofcode.com/2023/day/24

from dataclasses import dataclass
from util.segments import Segment1D
from sympy import solve, Symbol

epsilon = 1e-8

day_title = "Never Tell Me The Odds"

example_input = """
19, 13, 30 @ -2,  1, -2
18, 19, 22 @ -1, -1, -2
20, 25, 34 @ -2, -2, -4
12, 31, 28 @ -1, -2, -1
20, 19, 15 @  1, -5, -3
""".strip()


@dataclass
class HailStone:
    px: int
    py: int
    pz: int
    vx: int
    vy: int
    vz: int

    def __init__(self, string: str):
        position, velocity = string.split(" @ ")
        self.px, self.py, self.pz = map(int, position.split(", "))
        self.vx, self.vy, self.vz = map(int, velocity.split(", "))

    def __str__(self):
        return f"{self.px}, {self.py}, {self.pz} @ {self.vx}, {self.vy}, {self.vz}"

    def position_at(self, t):
        return (self.px + self.vx * t, self.py + self.vy * t, self.pz + self.vz * t)

    def path_intersection_xy(self, other: "HailStone"):
        # A * t = B for t = intersection moment of self
        A = self.vx * other.vy - self.vy * other.vx
        if A == 0:
            # parallel lines
            return None
        B = other.vy * (other.px - self.px) - other.vx * (other.py - self.py)
        t = B / A
        if t < 0:
            return None
        x, y, _ = self.position_at(t)
        if other.vx != 0:
            other_t = (x - other.px) / other.vx
        elif other.vy != 0:
            other_t = (y - other.py) / other.vy
        if other_t < 0:
            return None
        return x, y


def count_path_intersections_in_range(hailstones, test_range):
    total = 0
    for i, hailstone in enumerate(hailstones[:-1]):
        for other in hailstones[i + 1 :]:
            pos = hailstone.path_intersection_xy(other)
            if pos is None:
                continue
            x, y = pos
            if x in test_range and y in test_range:
                total += 1
    return total


def part1(text_input: str):
    hailstones = [HailStone(line) for line in text_input.split("\n")]
    test_range = Segment1D(200000000000000, 400000000000000)
    total = count_path_intersections_in_range(hailstones, test_range)
    return total


def part2(text_input):
    hailstones = [HailStone(line) for line in text_input.split("\n")]

    # variables to describe the position and velocity of the stone we throw
    x = Symbol("x")
    y = Symbol("y")
    z = Symbol("z")
    vx = Symbol("vx")
    vy = Symbol("vy")
    vz = Symbol("vz")

    equations = []
    # at the collision point with stone 1 the following equalities hold:
    # x + vx * t1 = x1 + vx1 * t1
    # y + vy * t1 = y1 + vy1 * t1
    # z + vz * t1 = z1 + vz1 * t1
    # where t1 is the moment of collision with this stone
    # getting rid of t1 variable leaves 2 equations per stone

    # we're told that the solution exists
    # but with 300 stones it has way more equations than variables
    # so it's enough to use just a few
    for s in hailstones[:4]:
        equations.extend(
            [
                (x - s.px) * (vy - s.vy) - (y - s.py) * (vx - s.vx),
                (x - s.px) * (vz - s.vz) - (z - s.pz) * (vx - s.vx),
            ]
        )

    solution = solve(equations)[0]
    return solution[x] + solution[y] + solution[z]


def test_part1():
    hailstones = [HailStone(line) for line in example_input.split("\n")]
    assert count_path_intersections_in_range(hailstones, Segment1D(7, 27)) == 2


def test_path_intersection():
    sa = HailStone("19, 13, 30 @ -2, 1, -2")
    sb = HailStone("18, 19, 22 @ -1, -1, -2")
    x, y = sa.path_intersection_xy(sb)
    assert abs(x - 14 - 1 / 3) < epsilon and abs(y - 15 - 1 / 3) < epsilon
    sa = HailStone("19, 13, 30 @ -2, 1, -2")
    sb = HailStone("20, 25, 34 @ -2, -2, -4")
    x, y = sa.path_intersection_xy(sb)
    assert abs(x - 11 - 2 / 3) < epsilon and abs(y - 16 - 2 / 3) < epsilon
    sa = HailStone("19, 13, 30 @ -2, 1, -2")
    sb = HailStone("12, 31, 28 @ -1, -2, -1")
    x, y = sa.path_intersection_xy(sb)
    assert abs(x - 6.2) < epsilon and abs(y - 19.4) < epsilon
    sa = HailStone("19, 13, 30 @ -2, 1, -2")
    sb = HailStone("20, 19, 15 @ 1, -5, -3")
    assert sa.path_intersection_xy(sb) is None


def test_part2():
    assert part2(example_input) == 47
