# Problem statement: https://adventofcode.com/2024/day/3

import re

day_title = "Mull It Over"


def part1(text_input: str) -> int:
    expr = re.compile(r"mul\((\d{1,3}),(\d{1,3})\)")
    pairs = re.findall(expr, text_input)
    answer = sum(int(a) * int(b) for a, b in pairs)
    return answer


def part2(text_input: str) -> int:
    expr = re.compile(r"mul\((\d{1,3}),(\d{1,3})\)|(do\(\))|(don\'t\(\))")
    instructions = re.findall(expr, text_input)
    enabled = True
    total = 0
    for num1, num2, do, dont in instructions:
        if do == "do()":
            enabled = True
        elif dont == "don't()":
            enabled = False
        elif enabled:
            total += int(num1) * int(num2)
    return total


test_input = """
xmul(2,4)%&mul[3,7]!@^do_not_mul(5,5)+mul(32,64]then(mul(11,8)mul(8,5))
""".strip()

test_input_2 = """
xmul(2,4)&mul[3,7]!^don't()_mul(5,5)+mul(32,64](mul(11,8)undo()?mul(8,5))
""".strip()


def test_part1():
    assert part1(test_input) == 161


def test_part2():
    assert part2(test_input_2) == 48
