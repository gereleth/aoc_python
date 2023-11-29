# Problem statement: https://adventofcode.com/2015/day/3

from util.inputs import movechars_dx_dy

day_title = "Perfectly Spherical Houses in a Vacuum"


def part1(text_input):
    x, y = 0, 0
    visited = set([(x, y)])
    for char in text_input:
        dx, dy = movechars_dx_dy[char]
        x += dx
        y += dy
        visited.add((x, y))
    return len(visited)


def test_part_1():
    assert part1(">") == 2
    assert part1("^v") == 2
    assert part1("^>v<") == 4
    assert part1("^v^v^v^v^v") == 2


def part2(text_input):
    x, y = 0, 0
    rx, ry = 0, 0
    visited = set([(x, y)])
    for i, char in enumerate(text_input):
        dx, dy = movechars_dx_dy[char]
        if i % 2 == 0:
            x += dx
            y += dy
            visited.add((x, y))
        else:
            rx += dx
            ry += dy
            visited.add((rx, ry))
    return len(visited)


def test_part_2():
    assert part2(">") == 2
    assert part2("^v") == 3
    assert part2("^>v<") == 3
    assert part2("^v^v^v^v^v") == 11
