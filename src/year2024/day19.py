# Problem statement: https://adventofcode.com/2024/day/19

from collections import Counter, defaultdict

day_title = "Linen Layout"


def parse_input(text_input: str):
    # index towels by their first letter to limit iterations we need to do later
    # some kind of tree could be even better maybe?
    towels, designs = text_input.split("\n\n")
    towels = towels.split(", ")
    towels_index = defaultdict(list)
    for towel in towels:
        towels_index[towel[0]].append(towel)
    designs = designs.split()
    return towels_index, designs


def part1(text_input: str) -> int:
    towels_index, designs = parse_input(text_input)
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
            for towel in towels_index[tail[0]]:
                if tail.startswith(towel) and canmake[tail[len(towel) :]]:
                    canmake[tail] = True
                    break
        total += canmake[design]
    return total


def part2(text_input: str) -> int:
    towels_index, designs = parse_input(text_input)
    total = 0

    ways = Counter()
    ways[""] = 1
    # same as part1 but collect counts and can't break early
    for design in designs:
        for i in range(1, len(design) + 1):
            tail = design[-i:]
            if tail in ways:
                continue
            for towel in towels_index[tail[0]]:
                if tail.startswith(towel):
                    ways[tail] += ways[tail[len(towel) :]]
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
