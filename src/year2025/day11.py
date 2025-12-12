# Problem statement: https://adventofcode.com/2025/day/11

from collections import defaultdict
from functools import cache

day_title = "Reactor"


def make_path_counter(text_input: str):
    edges = defaultdict(set)

    for line in text_input.split("\n"):
        a, bs = line.split(": ")
        edges[a].update(bs.split())

    @cache
    def count_paths(start, finish):
        total = 0
        for nxt in edges[start]:
            total += 1 if nxt == finish else count_paths(nxt, finish)
        return total

    return count_paths


def part1(text_input: str) -> int:
    count_paths = make_path_counter(text_input)
    total = count_paths("you", "out")
    return total


def part2(text_input: str) -> int:
    count_paths = make_path_counter(text_input)

    svr_to_fft = count_paths("svr", "fft")
    svr_to_dac = count_paths("svr", "dac")
    fft_to_dac = count_paths("fft", "dac")
    dac_to_fft = count_paths("dac", "fft")
    dac_to_out = count_paths("dac", "out")
    fft_to_out = count_paths("fft", "out")

    total = svr_to_fft * fft_to_dac * dac_to_out + svr_to_dac * dac_to_fft * fft_to_out
    return total


test_input = """
aaa: you hhh
you: bbb ccc
bbb: ddd eee
ccc: ddd eee fff
ddd: ggg
eee: out
fff: out
ggg: out
hhh: ccc fff iii
iii: out
""".strip("\n")


test_input_2 = """
svr: aaa bbb
aaa: fft
fft: ccc
bbb: tty
tty: ccc
ccc: ddd eee
ddd: hub
hub: fff
eee: dac
dac: fff
fff: ggg hhh
ggg: out
hhh: out
""".strip("\n")


def test_part1():
    assert part1(test_input) == 5


def test_part2():
    assert part2(test_input_2) == 2
