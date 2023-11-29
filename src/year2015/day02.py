# Problem statement: https://adventofcode.com/2015/day/2

day_title = "I Was Told There Would Be No Math"


def part1(text_input):
    total = 0
    for line in text_input.split():
        l, w, h = sorted(int(x) for x in line.split("x"))  # noqa: E741
        total += 3 * l * w + 2 * l * h + 2 * w * h
    return total


def part2(text_input):
    total = 0
    for line in text_input.split():
        l, w, h = sorted(int(x) for x in line.split("x"))  # noqa: E741
        total += 2 * l + 2 * w + w * l * h
    return total
