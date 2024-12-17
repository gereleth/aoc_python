# Problem statement: https://adventofcode.com/2024/day/17

import re

day_title = "Chronospatial Computer"


def part1(text_input: str) -> str:
    a, b, c, *program = map(int, re.findall(r"(\d+)", text_input))
    # print(a, b, c)
    # print(program)
    i = 0
    res = []
    while True:
        if i < 0 or i >= len(program) - 1:
            break
        opcode = program[i]
        operand = program[i + 1]

        combo = operand if operand <= 3 else [a, b, c][operand - 4]

        if opcode == 0:
            a = a // 2**combo
        elif opcode == 1:
            b = b ^ operand
        elif opcode == 2:
            b = combo % 8
        elif opcode == 3:
            if a > 0:
                i = operand
                continue
        elif opcode == 4:
            b = b ^ c
        elif opcode == 5:
            res.append(combo % 8)
        elif opcode == 6:
            b = a // 2**combo
        elif opcode == 7:
            c = a // 2**combo
        i += 2
    return ",".join(map(str, res))


# This is kinda crazy and tailored to the input
# My input program is a loop where in every iteration
# the value of a is replaced with a//8.
# It ends when a becomes 0.
# Values of b and c get overwritten in every iteration
# so whatever they start with doesn't matter.
# At the last iteration starting value of a is a0 = 1..7
# (because a0 // 8 == 0)
# Use part1 code to check which numbers from 1..7 produce the correct last digit of the program
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

    a_i = set([0])
    answers = set()
    while a_i:
        a_iplus1 = set()
        for value in a_i:
            for remainder in range(8):
                a = value * 8 + remainder
                res = part1(text_input.replace(a0, str(a)))
                if program == res:
                    answers.add(a)
                    # print(f"{a} => {res} ***")
                elif program[-len(res) :] == res and a > value:
                    # print(f"{a} => {res}")
                    a_iplus1.add(a)
        a_i = a_iplus1
    return min(answers)


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
