# Problem statement: https://adventofcode.com/2024/day/11

from collections import Counter
from typing import Tuple, List
from functools import cache

day_title = "Plutonian Pebbles"


@cache
def blink(stone: int) -> Tuple[int]:
    if stone == 0:
        return (1,)
    s = str(stone)
    if len(s) % 2 == 0:
        n = len(s) // 2
        return (int(s[:n]), int(s[n:]))
    return (stone * 2024,)


def count_stones(stones: List[int], num_blinks: int) -> int:
    counts = Counter(stones)
    for _ in range(num_blinks):
        new_counts = Counter()
        for stone, count in counts.items():
            for new_stone in blink(stone):
                new_counts[new_stone] += count
        counts = new_counts
    return sum(counts.values())


def part1(text_input: str) -> int:
    stones = [int(i) for i in text_input.split()]
    res = count_stones(stones, 25)
    return res


def part2(text_input: str) -> int:
    stones = [int(i) for i in text_input.split()]
    res = count_stones(stones, 75)
    return res


test_input = """
125 17
""".strip()


def test_blink():
    assert blink(125) == [253000]
    assert blink(17) == [1, 7]
    assert blink(0) == [1]


def test_count_stones():
    assert count_stones([125, 17], 1) == 3
    assert count_stones([125, 17], 2) == 4
    assert count_stones([125, 17], 3) == 5
    assert count_stones([125, 17], 4) == 9

    assert count_stones([125, 17], 25) == 55312


def test_part1():
    assert part1(test_input) == 55312


def test_part2():
    assert part2(test_input) == 65601038650482
