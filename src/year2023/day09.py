# Problem statement: https://adventofcode.com/2023/day/9

day_title = "Mirage Maintenance"

example_input = """
0 3 6 9 12 15
1 3 6 10 15 21
10 13 16 21 30 45
""".strip()


def extrapolate_forward(values: list[int]):
    diffs = [list(values)]
    while True:
        last_diff = diffs[-1]
        if all((a == last_diff[0]) for a in last_diff[1:]):
            break
        new_diff = [b - a for a, b in zip(last_diff[:-1], last_diff[1:])]
        diffs.append(new_diff)
    while len(diffs) > 1:
        last_value = diffs.pop()[-1]
        last_diff = diffs[-1]
        last_diff.append(last_diff[-1] + last_value)
    return diffs[-1][-1]


def part1(text_input: str):
    total = 0
    for line in text_input.split("\n"):
        values = [int(i) for i in line.split()]
        total += extrapolate_forward(values)
    return total


def test_extrapolate_forward():
    assert extrapolate_forward([0, 3, 6, 9, 12, 15]) == 18
    assert extrapolate_forward([1, 3, 6, 10, 15, 21]) == 28
    assert extrapolate_forward([10, 13, 16, 21, 30, 45]) == 68


def test_part_1():
    assert part1(example_input) == 114


def extrapolate_backward(values: list[int]):
    diffs = [list(values)]
    while True:
        last_diff = diffs[-1]
        if all((a == last_diff[0]) for a in last_diff[1:]):
            break
        new_diff = [b - a for a, b in zip(last_diff[:-1], last_diff[1:])]
        diffs.append(new_diff)
    while len(diffs) > 1:
        first_value = diffs.pop()[0]
        last_diff = diffs[-1]
        last_diff.insert(0, last_diff[0] - first_value)
    return diffs[-1][0]


def test_extrapolate_backward():
    assert extrapolate_backward([0, 3, 6, 9, 12, 15]) == -3
    assert extrapolate_backward([1, 3, 6, 10, 15, 21]) == 0
    assert extrapolate_backward([10, 13, 16, 21, 30, 45]) == 5


def part2(text_input: str):
    total = 0
    for line in text_input.split("\n"):
        values = [int(i) for i in line.split()]
        total += extrapolate_backward(values)
    return total


def test_part_2():
    assert part2(example_input) == 2
