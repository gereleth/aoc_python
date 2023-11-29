# Problem statement: https://adventofcode.com/2015/day/1

day_title = "Not Quite Lisp"


def part1(text_input):
    up = text_input.count("(")
    down = len(text_input) - up
    return up - down


def part2(text_input):
    floor = 0
    for i, char in enumerate(text_input):
        if char == "(":
            floor += 1
        else:
            floor -= 1
        if floor == -1:
            return i + 1
