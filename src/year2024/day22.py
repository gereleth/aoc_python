# Problem statement: https://adventofcode.com/2024/day/22

import numpy as np

day_title = "Monkey Market"


def pseudorandom(n):
    n = (n ^ (n << 6)) & 16777215
    n = (n ^ (n >> 5)) & 16777215
    n = (n ^ (n << 11)) & 16777215
    return n


def part1(text_input: str) -> int:
    numbers = np.array([int(n) for n in text_input.split("\n")])
    for _ in range(2000):
        numbers = pseudorandom(numbers)
    return numbers.sum()


def part2(text_input):
    numbers = np.array([int(n) for n in text_input.split("\n")])
    N = len(numbers)
    sequences = -np.ones(shape=(N, 19, 19, 19, 19), dtype=np.int8)
    changes = np.zeros(shape=(N, 4), dtype=np.int8)
    last_price = numbers % 10
    ci = 0
    idx = np.arange(N)
    for _ in range(4):
        numbers = pseudorandom(numbers)
        prices = numbers % 10
        changes[:, ci] = prices - last_price + 9
        ci = (ci + 1) % 4
        last_price = prices
    for _ in range(2000 - 4):
        numbers = pseudorandom(numbers)
        prices = numbers % 10
        changes[:, ci] = prices - last_price + 9
        ci = (ci + 1) % 4
        last_price = prices
        s1 = changes[:, ci]
        s2 = changes[:, (ci + 1) % 4]
        s3 = changes[:, (ci + 2) % 4]
        s4 = changes[:, (ci + 3) % 4]
        before = sequences[idx, s1, s2, s3, s4]
        sequences[idx, s1, s2, s3, s4] = np.where(before == -1, prices, before)
    return sequences.clip(0, None).sum(0).max()


test_input = """
1
10
100
2024
""".strip()

test_input_2 = """
1
2
3
2024
""".strip()


def test_pseudorandom():
    assert pseudorandom(123) == 15887950
    assert pseudorandom(15887950) == 16495136
    assert pseudorandom(16495136) == 527345


def test_part1():
    assert part1("1") == 8685429
    assert part1(test_input) == 37327623


def test_part2():
    assert part2(test_input_2) == 23
