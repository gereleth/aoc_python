# Day 2: The Ideal Stocking Stuffer
# Problem statement: https://adventofcode.com/2015/day/2

from hashlib import md5
import pytest

day_title = "The Ideal Stocking Stuffer"


def find_number(key, start_chars):
    i = 0
    while True:
        i += 1
        test = md5((key + str(i)).encode()).hexdigest()
        if test.startswith(start_chars):
            return i


def part1(text_input):
    return find_number(text_input, "00000")


def part2(text_input):
    return find_number(text_input, "000000")


@pytest.mark.slow
def test_part1():
    assert part1("abcdef") == 609043
    assert part1("pqrstuv") == 1048970


@pytest.mark.slow
def test_part2():
    assert part2("abcdef") == 6742839
    assert part2("pqrstuv") == 5714438
