# Problem statement: https://adventofcode.com/2023/day/13

import numpy as np

day_title = "Point of Incidence"

example_input_col = """
#.##..##.
..#.##.#.
##......#
##......#
..#.##.#.
..##..##.
#.#.##.#.
""".strip()

example_input_row = """
#...##..#
#....#..#
..##..###
#####.##.
#####.##.
..##..###
#....#..#
""".strip()


def parse(text):
    lines = text.split("\n")
    field = np.zeros((len(lines), len(lines[0])), int)
    for r, line in enumerate(lines):
        for c, char in enumerate(line):
            if char == "#":
                field[r, c] = 1
    return field


def find_row_reflection(field, smudge=0):
    R = field.shape[0]
    for r in range(1, R):
        num_rows = min(r, R - r)
        above = field[r - num_rows : r, :][::-1, :]
        below = field[r : r + num_rows, :]
        if np.abs(above - below).sum() == smudge:
            return r
    return -1


def find_col_reflection(field, smudge=0):
    return find_row_reflection(field.T, smudge=smudge)


def test_find_row():
    field = parse(example_input_row)
    r = find_row_reflection(field)
    assert r == 4


def test_find_col():
    field = parse(example_input_col)
    r = find_col_reflection(field)
    assert r == 5


def count_reflections(text_input, smudge=0):
    texts = text_input.split("\n\n")
    total = 0
    for text in texts:
        field = parse(text)
        r = find_row_reflection(field, smudge=smudge)
        if r >= 0:
            total += 100 * r
        else:
            c = find_col_reflection(field, smudge=smudge)
            if c < 0:
                print(field)
                raise ValueError("no reflections")
            total += c
    return total


def part1(text_input):
    return count_reflections(text_input)


def part2(text_input):
    return count_reflections(text_input, smudge=1)


def test_part1():
    text_input = "\n\n".join([example_input_col, example_input_row])
    assert part1(text_input) == 405


def test_part2():
    text_input = "\n\n".join([example_input_col, example_input_row])
    assert part2(text_input) == 400
