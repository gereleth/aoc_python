# Problem statement: https://adventofcode.com/2025/day/9

import numpy as np
from io import StringIO

day_title = "Movie Theater"


def part1(text_input: str) -> int:
    reds = np.loadtxt(StringIO(text_input), delimiter=",", dtype=np.int64)
    xx = reds[:, [0]]
    yy = reds[:, [1]]
    areas = (abs(xx - xx.T) + 1) * (abs(yy - yy.T) + 1)
    return areas.max()


def part2(text_input: str) -> int:
    reds = np.loadtxt(StringIO(text_input), delimiter=",", dtype=np.int64)
    reds2 = np.roll(reds, 1, axis=0)
    borders = [
        (min(x1, x2), max(x1, x2), min(y1, y2), max(y1, y2))
        for x1, x2, y1, y2 in zip(reds[:, 0], reds2[:, 0], reds[:, 1], reds2[:, 1])
    ]
    xx = reds[:, [0]]
    yy = reds[:, [1]]
    areas = (abs(xx - xx.T) + 1) * (abs(yy - yy.T) + 1)
    triu = np.triu_indices(len(reds), 1)
    areas = areas[triu]
    sorted_idx = np.argsort(areas)[::-1]
    kcheck = 0
    for i in sorted_idx:
        a, b = triu[0][i], triu[1][i]
        x1, y1 = reds[a, :]
        x2, y2 = reds[b, :]
        # check if the rectangle is all inside
        # by checking if it has borders in its inner part
        # (borders on border are ok)
        inner_x1 = min(x1, x2) + 1
        inner_x2 = max(x1, x2) - 1
        inner_y1 = min(y1, y2) + 1
        inner_y2 = max(y1, y2) - 1
        has_borders_inside = False
        for k in (*range(kcheck, len(borders)), *range(kcheck)):
            x1, x2, y1, y2 = borders[k]
            if not (x1 > inner_x2 or x2 < inner_x1 or y1 > inner_y2 or y2 < inner_y1):
                has_borders_inside = True
                kcheck = k
                break
        if not has_borders_inside:
            return areas[i]
    return 0


test_input = """
7,1
11,1
11,7
9,7
9,5
2,5
2,3
7,3
""".strip("\n")


def test_part1():
    assert part1(test_input) == 50


def test_part2():
    assert part2(test_input) == 24
