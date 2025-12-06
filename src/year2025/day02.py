# Problem statement: https://adventofcode.com/2025/day/2

import re
import heapq

day_title = "Gift Shop"


def parse_input(text_input: str):
    ranges = []
    for range_string in text_input.split(","):
        start, stop = range_string.split("-")
        ranges.append((int(start), int(stop)))
    return sorted(ranges)


# Slow solutions check every ID in the ranges
# Turn each ID into a string and check if it fits the invalid patterns


def part1_slow_strings(text_input: str) -> int:
    total = 0
    ranges = parse_input(text_input)
    for start, stop in ranges:
        for id in range(start, stop + 1):
            id_str = str(id)
            midpoint = len(id_str) // 2
            if id_str[:midpoint] == id_str[midpoint:]:
                total += id
    return total


def part2_slow_strings(text_input: str) -> int:
    total = 0
    ranges = parse_input(text_input)
    for start, stop in ranges:
        for id in range(start, stop + 1):
            id_str = str(id)
            str_len = len(id_str)
            midpoint = str_len // 2
            for plen in range(1, midpoint + 1):
                if str_len % plen == 0 and id_str[:plen] * (str_len // plen) == id_str:
                    total += id
                    break
    return total


# Same approach but use a regex to check patterns
# much less verbose but actually works slower


def part1_slow_regex(text_input: str) -> int:
    pattern = re.compile(r"^(\d+)\1{1}$")
    total = 0
    ranges = parse_input(text_input)
    for start, stop in ranges:
        for id in range(start, stop + 1):
            if re.match(pattern, str(id)):
                total += id
    return total


def part2_slow_regex(text_input: str) -> int:
    total = 0
    pattern = re.compile(r"^(\d+)\1+$")
    ranges = parse_input(text_input)
    for start, stop in ranges:
        for id in range(start, stop + 1):
            if re.match(pattern, str(id)):
                total += id
    return total


# Faster solutions iterate over invalid IDs
# and then check if the ID falls in ranges


def invalid_ids_gen(repeats=2):
    part = 1
    multiplier = 10
    while True:
        id = sum(part * multiplier**i for i in range(repeats))
        yield id
        part += 1
        if part >= multiplier:
            multiplier *= 10


# This keeps part 2 invalid IDs in sorted order and prevents double counting
# (for example, 222222 is both '22'*3 and '222'*2)
def merge_gen(generators):
    iterators = [iter(gen) for gen in generators]
    values = [(next(it), i) for i, it in enumerate(iterators)]
    heapq.heapify(values)
    last_yielded = None
    while True:
        value, index = heapq.heappop(values)
        if value != last_yielded:
            yield value
            last_yielded = value
        heapq.heappush(values, (next(iterators[index]), index))


def part1_generators(text_input: str) -> int:
    ranges = parse_input(text_input)
    total = 0
    range_index = 0
    for id in invalid_ids_gen(repeats=2):
        while id > ranges[range_index][1]:
            range_index += 1
            if range_index >= len(ranges):
                return total
        if id >= ranges[range_index][0]:
            total += id
    return total


def part2_generators(text_input: str) -> int:
    ranges = parse_input(text_input)
    max_id = ranges[-1][1]
    max_repeats = len(str(max_id))
    total = 0
    ids_gen = merge_gen(
        invalid_ids_gen(repeats=repeats) for repeats in range(2, max_repeats + 1)
    )
    range_index = 0
    for id in ids_gen:
        while id > ranges[range_index][1]:
            range_index += 1
            if range_index >= len(ranges):
                return total
        if id >= ranges[range_index][0]:
            total += id
    return total


def part1(text_input: str) -> int:
    return part1_generators(text_input)


def part2(text_input: str) -> int:
    return part2_generators(text_input)


test_input = """
11-22,95-115,998-1012,1188511880-1188511890,222220-222224,1698522-1698528,446443-446449,38593856-38593862,565653-565659,824824821-824824827,2121212118-2121212124
""".strip()


def test_part1():
    assert part1_slow_strings(test_input) == 1227775554
    assert part1_slow_regex(test_input) == 1227775554
    assert part1_generators(test_input) == 1227775554


def test_part2():
    assert part2_slow_strings(test_input) == 4174379265
    assert part2_slow_regex(test_input) == 4174379265
    assert part2_generators(test_input) == 4174379265
