# Problem statement: https://adventofcode.com/2023/day/1

import re

day_title = "Trebuchet?!"


def part1(text_input):
    total = 0
    for line in text_input.split("\n"):
        digits = re.findall(r"\d", line)
        total += int(digits[0] + digits[-1])
    return total


spelled_numbers = "one two three four five six seven eight nine"
spelled_to_digit = {x: str(i + 1) for i, x in enumerate(spelled_numbers.split())}
pattern = "|".join(spelled_numbers.split() + [r"\d"])
expr = re.compile(f"(?=({pattern}))")


def part2(text_input):
    total = 0
    for line in text_input.split("\n"):
        digit_like = re.findall(expr, line)
        first = spelled_to_digit.get(digit_like[0], digit_like[0])
        last = spelled_to_digit.get(digit_like[-1], digit_like[-1])
        total += int(first + last)
    return total


def test_part2():
    assert part2("seven") == 77
    assert part2("sixeight") == 68
    assert part2("twone") == 21
    assert part2("1fiveight") == 18
    assert part2("twone2") == 22
    assert part2("xxtwone2xx") == 22
