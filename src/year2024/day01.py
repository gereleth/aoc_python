# Problem statement: https://adventofcode.com/2024/day/1

from collections import Counter
from typing import List, Tuple

day_title = "Historian Hysteria"


def parse_input(text_input: str) -> Tuple[List[int], List[int]]:
    numbers = text_input.split()
    list1 = [int(i) for i in numbers[0::2]]
    list2 = [int(i) for i in numbers[1::2]]
    return list1, list2


def part1(text_input: str) -> int:
    list1, list2 = parse_input(text_input)
    list1.sort()
    list2.sort()
    answer = sum(abs(a - b) for a, b in zip(list1, list2))
    return answer


def part2(text_input: str) -> int:
    list1, list2 = parse_input(text_input)
    counter = Counter(list2)
    answer = sum(a * counter[a] for a in list1)
    return answer


test_input = """
3   4
4   3
2   5
1   3
3   9
3   3
""".strip()


def test_parse_input():
    list1, list2 = parse_input(test_input)
    assert list1 == [3, 4, 2, 1, 3, 3]
    assert list2 == [4, 3, 5, 3, 9, 3]


def test_part1():
    assert part1(test_input) == 11


def test_part2():
    assert part2(test_input) == 31
