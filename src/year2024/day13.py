# Problem statement: https://adventofcode.com/2024/day/13

import re

day_title = "Claw Contraption"


class ClawContraption:
    def __init__(self, text):
        ax, ay, bx, by, px, py = re.findall(r"(\d+)", text)
        self.ax, self.ay = int(ax), int(ay)
        self.bx, self.by = int(bx), int(by)
        self.px, self.py = int(px), int(py)
        self.cost_a = 3
        self.cost_b = 1

    def min_tokens(self, max_actions=None):
        # solving a system of linear equations for ta, tb
        # ta * ax + tb * bx = px
        # ta * ay + tb * by = py
        A = self.bx * self.ay - self.by * self.ax
        B = self.bx * self.py - self.by * self.px
        if B % A != 0:
            return 0
        ta = B // A
        C = self.px - self.ax * ta
        if C % self.bx != 0:
            return 0
        tb = C // self.bx
        if ta < 0 or tb < 0:
            return 0
        if max_actions is not None and (ta > max_actions or tb > max_actions):
            return 0
        return ta * self.cost_a + tb * self.cost_b


def part1(text_input: str) -> int:
    machines = text_input.split("\n\n")
    total = 0
    for machine in machines:
        claw = ClawContraption(machine)
        total += claw.min_tokens(max_actions=100)
    return total


def part2(text_input: str) -> int:
    machines = text_input.split("\n\n")
    delta = 10000000000000
    total = 0
    for machine in machines:
        claw = ClawContraption(machine)
        claw.px += delta
        claw.py += delta
        total += claw.min_tokens()
    return total


test_input = """
Button A: X+94, Y+34
Button B: X+22, Y+67
Prize: X=8400, Y=5400

Button A: X+26, Y+66
Button B: X+67, Y+21
Prize: X=12748, Y=12176

Button A: X+17, Y+86
Button B: X+84, Y+37
Prize: X=7870, Y=6450

Button A: X+69, Y+23
Button B: X+27, Y+71
Prize: X=18641, Y=10279
""".strip()

test_input_2 = """

""".strip()


def test_part1():
    assert part1(test_input) == 480


def test_part2():
    assert part2(test_input) == 875318608908
