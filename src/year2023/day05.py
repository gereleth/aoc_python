# Problem statement: https://adventofcode.com/2023/day/5

import re
from typing import List
from util.segments import Segment1D

day_title = "If You Give A Seed A Fertilizer"

example_input = """
seeds: 79 14 55 13

seed-to-soil map:
50 98 2
52 50 48

soil-to-fertilizer map:
0 15 37
37 52 2
39 0 15

fertilizer-to-water map:
49 53 8
0 11 42
42 0 7
57 7 4

water-to-light map:
88 18 7
18 25 70

light-to-temperature map:
45 77 23
81 45 19
68 64 13

temperature-to-humidity map:
0 69 1
1 0 69

humidity-to-location map:
60 56 37
56 93 4
""".strip()


class TranslateRange:
    def __init__(self, destination_start: int, source_start: int, length: int):
        self.delta = destination_start - source_start
        self.segment = Segment1D(source_start, source_start + length - 1)

    def __lt__(self, other):
        return self.segment < other.segment

    def transform_point(self, point):
        if point in self.segment:
            return point + self.delta
        else:
            return None

    def transform_range(self, segment: "Segment1D"):
        results = []
        leftovers = []
        if self.segment.intersects(segment):
            transformed = self.segment.intersection(segment)
            transformed.a += self.delta
            transformed.b += self.delta
            results.append(transformed)
            leftovers.extend(segment.difference(self.segment))
        else:
            leftovers.append(segment)
        return results, leftovers


def test_translate_range_point():
    r = TranslateRange(50, 98, 2)
    assert r.transform_point(97) is None
    assert r.transform_point(98) == 50
    assert r.transform_point(99) == 51
    assert r.transform_point(100) is None


def test_translate_range_range():
    r = TranslateRange(50, 98, 2)
    s = Segment1D(97, 100)
    results, leftovers = r.transform_range(s)
    assert len(results) == 1
    assert results[0] == Segment1D(50, 51)
    assert len(leftovers) == 2
    assert min(leftovers) == Segment1D(97, 97)
    assert max(leftovers) == Segment1D(100, 100)


class AlmanacMap:
    def __init__(self, ranges: List["TranslateRange"]):
        self.ranges = sorted(ranges)

    def transform_point(self, point):
        for r in self.ranges:
            res = r.transform_point(point)
            if res is not None:
                return res
        return point

    def transform_ranges(self, segments: List["Segment1D"]):
        todo = sorted(segments)
        transformed = []
        notfound = []
        while len(todo) > 0:
            segment = todo.pop()
            found = False
            for r in self.ranges:
                res, left = r.transform_range(segment)
                if len(res) > 0:
                    found = True
                    transformed.extend(res)
                    todo.extend(left)
                    break
            if not found:
                notfound.append(segment)
        return transformed + notfound


def test_almanac_map_transform_point():
    r1 = TranslateRange(50, 98, 2)
    r2 = TranslateRange(52, 50, 48)
    alm = AlmanacMap([r1, r2])
    assert alm.transform_point(49) == 49
    assert alm.transform_point(50) == 52
    assert alm.transform_point(97) == 99
    assert alm.transform_point(98) == 50
    assert alm.transform_point(99) == 51
    assert alm.transform_point(100) == 100


def test_almanac_map_transform_ranges():
    r1 = TranslateRange(50, 98, 2)
    r2 = TranslateRange(52, 50, 48)
    alm = AlmanacMap([r1, r2])
    todo = [Segment1D(40, 60)]
    done = alm.transform_ranges(todo)
    assert len(done) == 2
    assert min(done) == Segment1D(40, 49)
    assert max(done) == Segment1D(52, 62)


def parse_input(text_input):
    seeds, *maps = text_input.split("\n\n")
    seeds = [int(i) for i in re.findall(r"(\d+)", seeds)]
    almanac = {}
    sequence = {}
    for mapp in maps:
        lines = mapp.split("\n")
        source, destination = lines[0].split()[0].split("-to-")
        sequence[source] = destination
        ranges = []
        for line in lines[1:]:
            destination_index, source_index, length = [int(i) for i in line.split()]
            r = TranslateRange(destination_index, source_index, length)
            ranges.append(r)
        almanac[source] = AlmanacMap(ranges)
    return seeds, almanac, sequence


def part1(text_input):
    seeds, almanac, sequence = parse_input(text_input)
    locations = []
    for seed in seeds:
        value = seed
        a = "seed"
        while a != "location":
            mapp = almanac[a]
            a = sequence[a]
            value = mapp.transform_point(value)
        locations.append(value)
    return min(locations)


def test_part_1():
    assert part1(example_input) == 35


def part2(text_input):
    seeds, almanac, sequence = parse_input(text_input)
    todo = []
    for seed_start, seed_len in zip(seeds[0::2], seeds[1::2]):
        todo.append(Segment1D(seed_start, seed_start + seed_len - 1))

    a = "seed"
    while a != "location":
        mapp = almanac[a]
        todo = mapp.transform_ranges(todo)
        a = sequence[a]

    min_loc = min([segment.a for segment in todo])
    return min_loc


def test_part_2():
    assert part2(example_input) == 46
