# Problem statement: https://adventofcode.com/2023/day/6

from math import sqrt, ceil, floor

day_title = "Wait For It"

example_input = """
Time:      7  15   30
Distance:  9  40  200
""".strip()


def ways_to_win(time: int, distance: int):
    discr = sqrt(time**2 - 4 * distance) / 2
    tmax = floor(0.5 * time + discr)
    if tmax * (time - tmax) == distance:
        tmax -= 1
    tmin = ceil(0.5 * time - discr)
    if tmin * (time - tmin) == distance:
        tmin += 1
    return tmax - tmin + 1


def part1(text_input):
    time, distance = text_input.split("\n")
    time = time.split(":")[1].strip().split()
    distance = distance.split(":")[1].strip().split()
    total = 1
    for t, d in zip(time, distance):
        total *= ways_to_win(int(t), int(d))
    return total


def part2(text_input):
    time, distance = text_input.split("\n")
    time = "".join(time.split(":")[1].split())
    distance = "".join(distance.split(":")[1].split())
    total = ways_to_win(int(time), int(distance))
    return total


def test_part_1():
    assert part1(example_input) == 288


def test_part_2():
    assert part2(example_input) == 71503
