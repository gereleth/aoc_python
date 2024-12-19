# Problem statement: https://adventofcode.com/2024/day/19

from collections import Counter, defaultdict
from typing import Iterator

day_title = "Linen Layout"


# A data structure for quick iteration over towels that a particular
# design could start with
class PentacolorTree:
    def __init__(self):
        self.is_leaf = False
        self.children = defaultdict(PentacolorTree)

    def put(self, value: str) -> None:
        """Add a towel to the tree"""
        if len(value) == 0:
            self.is_leaf = True
        else:
            child = self.children[value[0]]
            child.put(value[1:])

    def get_splits(self, value: str) -> Iterator[tuple[str, str]]:
        """Splits string into `towel+rest` for all towels that fit"""
        tree = self
        for i, char in enumerate(value):
            if char not in tree.children:
                break
            tree = tree.children[char]
            if tree.is_leaf:
                yield value[: i + 1], value[i + 1 :]


def parse_input(text_input: str):
    towels, designs = text_input.split("\n\n")
    towels = towels.split(", ")
    # index towels into a tree structure
    towels_tree = PentacolorTree()
    for towel in towels:
        towels_tree.put(towel)
    designs = designs.split()
    return towels_tree, designs


def part1(text_input: str) -> int:
    towels_tree, designs = parse_input(text_input)
    total = 0
    # canmake is a dict like {design: can we make it}
    canmake = defaultdict(bool)
    canmake[""] = True
    for design in designs:
        # iterate though design backwards
        for i in range(1, len(design) + 1):
            tail = design[-i:]
            if tail in canmake:
                continue
            # see if `tail` is `some_towel + rest` where we can make `rest`
            for _, rest in towels_tree.get_splits(tail):
                if canmake[rest]:
                    canmake[tail] = True
                    break
        total += canmake[design]
    return total


def part2(text_input: str) -> int:
    towels_tree, designs = parse_input(text_input)
    total = 0

    ways = Counter()
    ways[""] = 1
    # same as part1 but collect counts and can't break early
    for design in designs:
        for i in range(1, len(design) + 1):
            tail = design[-i:]
            if tail in ways:
                continue
            for _, rest in towels_tree.get_splits(tail):
                ways[tail] += ways[rest]
        total += ways[design]
    return total


test_input = """
r, wr, b, g, bwu, rb, gb, br

brwrr
bggr
gbbr
rrbgbr
ubwu
bwurrg
brgr
bbrgwb
""".strip()


def test_part1():
    assert part1(test_input) == 6


def test_part2():
    assert part2(test_input) == 16
