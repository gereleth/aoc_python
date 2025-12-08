# Problem statement: https://adventofcode.com/2025/day/8

from itertools import combinations
import numpy as np
from scipy.spatial.distance import pdist
from io import StringIO

day_title = "Playground"


def get_sorted_pairs(boxes):
    distances = pdist(boxes, metric="euclidean")
    idx = np.argsort(distances)
    pairs = list(combinations(range(len(boxes)), 2))
    for i in idx:
        yield pairs[i]


# The connection logic can probably be much more efficient...


def part1(text_input: str, count=1000) -> int:
    boxes = np.loadtxt(StringIO(text_input), delimiter=",", dtype=np.int64)
    pairs = get_sorted_pairs(boxes)
    # connect pairs of boxes
    connections = {i: {i} for i in range(len(boxes))}
    for n, (i, j) in enumerate(pairs):
        conn = connections[i]
        conn.update(connections[j])
        for b in conn:
            connections[b] = conn
        if n == count - 1:
            break
    sizes = []
    # get connected component sizes
    while connections:
        i, boxes = connections.popitem()
        sizes.append(len(boxes))
        boxes.remove(i)
        for b in boxes:
            connections.pop(b)
    sizes.sort(reverse=True)
    return sizes[0] * sizes[1] * sizes[2]


def part2(text_input: str) -> int:
    boxes = np.loadtxt(StringIO(text_input), delimiter=",", dtype=np.int64)
    pairs = get_sorted_pairs(boxes)
    # connect until all in
    connections = {i: {i} for i in range(len(boxes))}
    for _, (i, j) in enumerate(pairs):
        conn = connections[i]
        conn.update(connections[j])
        if len(conn) == len(boxes):
            return boxes[i][0] * boxes[j][0]
        for b in conn:
            connections[b] = conn


test_input = """
162,817,812
57,618,57
906,360,560
592,479,940
352,342,300
466,668,158
542,29,236
431,825,988
739,650,466
52,470,668
216,146,977
819,987,18
117,168,530
805,96,715
346,949,466
970,615,88
941,993,340
862,61,35
984,92,344
425,690,689
""".strip("\n")


def test_part1():
    assert part1(test_input, count=10) == 40


def test_part2():
    assert part2(test_input) == 25272
