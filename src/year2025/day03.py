# Problem statement: https://adventofcode.com/2025/day/3

day_title = "Lobby"


def max_number_from_digits(digits: list[int], count: int) -> int:
    N = len(digits)
    number = 0
    start = 0
    for place in range(count):
        places_left = count - 1 - place
        digit = max(digits[start : N - places_left])
        start = digits.index(digit, start) + 1
        number += digit * 10**places_left
    return number


def part1(text_input: str) -> int:
    total = 0
    for battery_bank in text_input.split():
        digits = [int(c) for c in battery_bank]
        total += max_number_from_digits(digits, 2)
    return total


def part2(text_input: str) -> int:
    total = 0
    for battery_bank in text_input.split():
        digits = [int(c) for c in battery_bank]
        total += max_number_from_digits(digits, 12)
    return total


test_input = """
987654321111111
811111111111119
234234234234278
818181911112111
""".strip()


def test_part1():
    assert part1(test_input) == 357


def test_part2():
    assert part2(test_input) == 3121910778619
