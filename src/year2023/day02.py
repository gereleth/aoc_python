# Problem statement: https://adventofcode.com/2023/day/2

from collections import defaultdict

day_title = "Cube Conundrum"

example_input = """
Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green
Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue
Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red
Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red
Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green
""".strip()

LIMIT = {"red": 12, "green": 13, "blue": 14}


def is_possible(rounds):
    rounds = rounds.split(";")
    max_counts = defaultdict(int)
    for round in rounds:
        balls = round.split(",")
        for ball in balls:
            count, color = ball.split()
            count = int(count)
            max_counts[color] = max(max_counts[color], count)
            if max_counts[color] > LIMIT[color]:
                return False
    return True


def part1(text_input):
    total = 0
    for line in text_input.split("\n"):
        game, rounds = line.split(": ")
        if is_possible(rounds):
            game_id = int(game.split()[1])
            total += game_id
    return total


def test_part_1():
    assert part1(example_input) == 8


def game_power(rounds):
    rounds = rounds.split(";")
    max_counts = defaultdict(int)
    for round in rounds:
        balls = round.split(",")
        for x in balls:
            count, color = x.split()
            count = int(count)
            max_counts[color] = max(max_counts[color], count)
    power = 1
    for count in max_counts.values():
        power *= count
    return power


def part2(text_input):
    total = 0
    for line in text_input.split("\n"):
        _, rounds = line.split(": ")
        total += game_power(rounds)
    return total


def test_part_2():
    assert part2(example_input) == 2286
