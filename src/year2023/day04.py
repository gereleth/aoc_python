# Problem statement: https://adventofcode.com/2023/day/4

day_title = "Scratchcards"

example_input = """
Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53
Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19
Card 3:  1 21 53 59 44 | 69 82 63 72 16 21 14  1
Card 4: 41 92 73 84 69 | 59 84 76 51 58  5 54 83
Card 5: 87 83 26 28 32 | 88 30 70 12 93 22 82 36
Card 6: 31 18 13 56 72 | 74 77 10 23 35 67 36 11
""".strip()


def count_matches(line):
    card, nums = line.split(": ")
    win, have = nums.split(" | ")
    win = set(int(x) for x in win.split())
    have = set(int(x) for x in have.split())
    matches = len(have.intersection(win))
    return matches


def part1(text_input):
    total = 0
    lines = text_input.split("\n")
    for i, line in enumerate(lines):
        matches = count_matches(line)
        if matches > 0:
            total += 2 ** (matches - 1)
    return total


def test_part_1():
    assert part1(example_input) == 13


def part2(text_input):
    lines = text_input.split("\n")
    copies = [1] * len(lines)
    for i, line in enumerate(lines):
        matches = count_matches(line)
        for k in range(matches):
            copies[i + k + 1] += copies[i]
    return sum(copies)


def test_part_2():
    assert part2(example_input) == 30
