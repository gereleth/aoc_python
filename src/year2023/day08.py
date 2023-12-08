# Problem statement: https://adventofcode.com/2023/day/8

# This task bugs me because the input is very carefully crafted
# with some properties you have no reason to expect. But they do
# make the solution easier.
# I tried to avoid relying on the fact that all cycles in part 2 happen to
# start at the exact same moment. What was the chance of that?..

from math import lcm

day_title = "Haunted Wasteland"

example_input = """
RL

AAA = (BBB, CCC)
BBB = (DDD, EEE)
CCC = (ZZZ, GGG)
DDD = (DDD, DDD)
EEE = (EEE, EEE)
GGG = (GGG, GGG)
ZZZ = (ZZZ, ZZZ)
""".strip()


def parse_input(text_input: str):
    instructions, nodes_lines = text_input.split("\n\n")
    # left is 0, right is 1 so we can index destinations tuple with this value
    instructions = [int(i == "R") for i in instructions]
    # nodes[source] = (left_destination, right_destination)
    nodes = {}
    for line in nodes_lines.split("\n"):
        source, destinations = line.split(" = ")
        destinations = destinations[1:-1].split(", ")
        nodes[source] = tuple(destinations)
    return instructions, nodes


def part1(text_input):
    instructions, nodes = parse_input(text_input)
    location = "AAA"
    steps = 0
    N = len(instructions)
    while location != "ZZZ":
        move = instructions[steps % N]
        location = nodes[location][move]
        steps += 1
    return steps


def test_part_1():
    assert part1(example_input) == 2


example_input_2 = """
LR

11A = (11B, XXX)
11B = (XXX, 11Z)
11Z = (11B, XXX)
22A = (22B, XXX)
22B = (22C, 22C)
22C = (22Z, 22Z)
22Z = (22B, 22B)
XXX = (XXX, XXX)
""".strip()


def part2(text_input):
    instructions, nodes = parse_input(text_input)
    locations = [loc for loc in nodes.keys() if loc.endswith("A")]
    N = len(instructions)
    L = len(locations)
    steps = 0
    memory = [{} for _ in locations]
    periods = {}
    while not all(loc.endswith("Z") for loc in locations):
        move_index = steps % N
        move = instructions[move_index]
        # move
        for k, loc in enumerate(locations):
            locations[k] = nodes[loc][move]
        steps += 1
        # now see if we are at a finish point. Again.
        for k, loc in enumerate(locations):
            if k in periods:
                continue
            if loc.endswith("Z"):
                key = (loc, move_index)
                if key in memory[k]:
                    before = memory[k][key]
                    periods[k] = (steps, steps - before)
                else:
                    memory[k][key] = steps
        if len(periods) == L:
            # print(periods)
            break
    # are we there yet?..
    if all(loc.endswith("Z") for loc in locations):
        return steps
    # at least we now know when each location repeats
    # just need to line up repetitions so they all happen simultaneously
    start0, period0 = periods[0]
    for i in range(1, L):
        start, period = periods[i]
        psteps = 0
        while True:
            # what if they never line up though... Like equal periods and different starts?..
            psteps += 1
            current = start0 + period0 * psteps
            dd = (current - start) % period
            if dd == 0:
                start0 = current
                period0 = lcm(period0, period)
                break
    return start0


def test_part_2():
    assert part2(example_input_2) == 6


# cycle starts do not align in this input
example_input_3 = """
L

00A = (A00, XXX)
A00 = (B00, XXX)
B00 = (00Z, XXX)
00Z = (001, XXX)
001 = (002, XXX)
002 = (003, XXX)
003 = (00Z, XXX)
11A = (11Z, XXX)
11Z = (111, XXX)
111 = (112, XXX)
112 = (113, XXX)
113 = (114, XXX)
114 = (11Z, XXX)
""".strip()


def test_part_2_unequal():
    assert part2(example_input_3) == 11
