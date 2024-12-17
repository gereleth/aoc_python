# Problem statement: https://adventofcode.com/2024/day/17

import re

day_title = "Chronospatial Computer"


def part1(text_input: str) -> str:
    registers, program = text_input.split("\n\n")
    a, b, c = map(int, re.findall(r"(\d+)", registers))
    program = list(map(int, program.split()[1].split(",")))
    # print(a, b, c)
    # print(program)
    i = 0
    res = []
    while True:
        if i < 0 or i >= len(program) - 1:
            break
        opcode = program[i]
        operand = program[i + 1]

        combo = -1
        if operand <= 3:
            combo = operand
        else:
            combo = [a, b, c][operand - 4]

        if opcode == 0:
            numerator = a
            denominator = 2**combo
            a = numerator // denominator
            i += 2
        elif opcode == 1:
            b = b ^ operand
            i += 2
        elif opcode == 2:
            b = combo % 8
            i += 2
        elif opcode == 3:
            if a == 0:
                i += 2
            else:
                i = operand
        elif opcode == 4:
            b = b ^ c
            i += 2
        elif opcode == 5:
            res.append(combo % 8)
            i += 2
        elif opcode == 6:
            numerator = a
            denominator = 2**combo
            b = numerator // denominator
            i += 2
        elif opcode == 7:
            numerator = a
            denominator = 2**combo
            c = numerator // denominator
            i += 2
    return ",".join(map(str, res))


# This is kinda crazy and tailored to the input
# My input program is a loop where in every iteration
# the value of a is replaced with a//8.
# It ends when a becomes 0.
# Values of b and c get overwritten in every iteration
# so whatever they start with doesn't matter.
# At the last iteration starting value of a is a0 = 0..7
# (because a0 // 8 == 0)
# Use part1 code to check which numbers from 0..7 produce the correct last digit of the program
# At the iteration before that it's a1 = 8*a0 + (0..7)
# (because a1 // 8 == a0)
# And before that it's a2 = 8*a1 + (0..7)
# We can go through steps backwards and check if the output matches
# the tail of the input program
# Until we have a printed a complete program


def part2(text_input: str) -> int:
    registers, program = text_input.split("\n\n")
    a0 = re.findall(r"(\d+)", registers)[0]
    program = program.split()[1]

    base = set([0])
    totals = set()
    while base:
        new_base = set()
        for value in base:
            for ai in range(8):
                a = value * 8 + ai
                res = part1(text_input.replace(a0, str(a)))
                if program == res:
                    totals.add(a)
                    # print(f"{a} => {res} ***")
                elif program[-len(res) :] == res and a > value:
                    # print(f"{a} => {res}")
                    new_base.add(a)
        base = new_base
    return min(totals)


test_input = """
Register A: 729
Register B: 0
Register C: 0

Program: 0,1,5,4,3,0
""".strip()

test_input_2 = """
Register A: 117440
Register B: 0
Register C: 0

Program: 0,3,5,4,3,0
""".strip()


def test_part1():
    assert part1(test_input) == "4,6,3,5,6,3,5,2,1,0"
    assert part1(test_input_2) == "0,3,5,4,3,0"


def test_part2():
    assert part2(test_input_2) == 117440
