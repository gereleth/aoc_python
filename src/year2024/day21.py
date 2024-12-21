# Problem statement: https://adventofcode.com/2024/day/21
# Verbose as hell but this broke my brain

from functools import cache

day_title = "Keypad Conundrum"


class Keypad:
    def __init__(self, lines: list[str]):
        self.lines = lines
        self.R = len(lines)
        self.C = len(lines[0])
        self.button_positions = {}
        for r in range(self.R):
            for c in range(self.C):
                button = lines[r][c]
                self.button_positions[button] = (r, c)
                if button == "X":
                    self.gap = (r, c)

    @cache
    def moves(self, r0: int, c0: int, r: int, c: int):
        """Possible move directions for
        getting from button at (r0, c0) to button at (r, c)
        Returns list of tuples [(direction symbol, dr, dc)]
        """
        options = []
        if r > r0:
            options.append(("v", 1, 0))
        if r < r0:
            options.append(("^", -1, 0))
        if c < c0:
            options.append(("<", 0, -1))
        if c > c0:
            options.append((">", 0, 1))
        # Mind the gap
        options = [
            option for option in options if (r0 + option[1], c0 + option[2]) != self.gap
        ]
        return options

    @cache
    def basic_programs(self, button0: str, button: str):
        """Return all programs that make a keypad robot
        move from `button0` and press `button`"""
        if button0 == button:
            return ["A"]
        r0, c0 = self.button_positions[button0]
        r, c = self.button_positions[button]
        queue = [("", r0, c0)]
        res = []
        while queue:
            path, r0, c0 = queue.pop()
            if r0 == r and c0 == c:
                res.append(path + "A")
                continue
            moves = self.moves(r0, c0, r, c)
            for char, dr, dc in moves:
                queue.append((path + char, r0 + dr, c0 + dc))
        return res

    def controls_for_code(self, code):
        """Represent code as a sequence of "move from X and press Y"
        For each step yield a list of basic programs that accomplish it
        """
        for button1, button2 in zip("A" + code[:-1], code):
            yield self.basic_programs(button1, button2)


numeric_keypad = Keypad("789 456 123 X0A".split())
directional_keypad = Keypad("X^A <v>".split())


@cache
def best_controls_directional(code: str, level: int):
    """Find shortest sequence length to enter `code` on a directional keypad
    through `level` layers of directional keypads"""
    cost = 0
    for basic_programs in directional_keypad.controls_for_code(code):
        if level == 0:
            cost += min(len(program) for program in basic_programs)
        else:
            cost += min(
                (
                    best_controls_directional(program, level - 1)
                    for program in basic_programs
                )
            )
    return cost


def best_controls_numeric(code: str, levels: int):
    """Find shortest sequence length to enter `code` on a numeric keypad
    through `levels` directional keypads"""
    cost = 0
    for basic_programs in numeric_keypad.controls_for_code(code):
        cost += min(
            (
                best_controls_directional(program, level=levels - 1)
                for program in basic_programs
            )
        )
    return cost


def get_answer(text_input, levels=2):
    codes = text_input.split()
    total = 0
    for code in codes:
        res = best_controls_numeric(code, levels=levels)
        num = int("".join(a for a in code if a.isnumeric()))
        total += num * res
    return total


def part1(text_input: str) -> int:
    return get_answer(text_input, levels=2)


def part2(text_input: str) -> int:
    return get_answer(text_input, levels=25)


test_input = """
029A
980A
179A
456A
379A
""".strip()


def test_basic_programs_numeric():
    ps = set(numeric_keypad.basic_programs("A", "1"))
    assert ps == set(("<^<A", "^<<A"))
    ps = set(numeric_keypad.basic_programs("8", "3"))
    assert ps == set((">vvA", "v>vA", "vv>A"))


def test_basic_programs_directional():
    ps = set(directional_keypad.basic_programs("A", "<"))
    assert ps == set(("v<<A", "<v<A"))
    ps = set(directional_keypad.basic_programs("<", "^"))
    assert ps == set((">^A",))


def test_best_control_1():
    assert best_controls_numeric("029A", 2) == 68
    assert best_controls_numeric("980A", 2) == 60
    assert best_controls_numeric("179A", 2) == 68
    assert best_controls_numeric("456A", 2) == 64
    assert best_controls_numeric("379A", 2) == 64


def test_part_1():
    assert part1(test_input) == 126384


def test_part_2():
    assert part2(test_input) == 154115708116294
