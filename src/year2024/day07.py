# Problem statement: https://adventofcode.com/2024/day/7

from typing import List, Tuple

day_title = "Bridge Repair"


def parse_input(text_input: str) -> List[Tuple[int, List[int]]]:
    lines = text_input.split("\n")
    data = []
    for line in lines:
        result, nums = line.split(": ")
        result = int(result)
        nums = list(map(int, nums.split()))
        data.append((result, nums))
    return data


def is_possible(result: int, nums: List[int], operators="+*") -> bool:
    nums = nums[::-1]
    calcs = [nums.pop()]
    while len(nums) > 0:
        new_calcs = []
        num = nums.pop()
        for calc in calcs:
            for op in operators:
                if op == "+":
                    new = calc + num
                elif op == "*":
                    new = calc * num
                else:
                    new = int(str(calc) + str(num))
                if new == result and len(nums) == 0:
                    return True
                elif new < result:
                    new_calcs.append(new)
        calcs = new_calcs
    return False


def part1(text_input: str) -> int:
    data = parse_input(text_input)
    total = 0
    for result, nums in data:
        if is_possible(result, nums):
            total += result
    return total


def part2(text_input: str) -> int:
    data = parse_input(text_input)
    total = 0
    for result, nums in data:
        if is_possible(result, nums):
            total += result
        elif is_possible(result, nums, operators="|+*"):
            total += result
    return total


test_input = """
190: 10 19
3267: 81 40 27
83: 17 5
156: 15 6
7290: 6 8 6 15
161011: 16 10 13
192: 17 8 14
21037: 9 7 18 13
292: 11 6 16 20
""".strip()


def test_part1():
    lines = test_input.split("\n")
    assert part1(lines[0]) == 190
    assert part1(lines[1]) == 3267
    assert part1(lines[2]) == 0
    assert part1(lines[3]) == 0
    assert part1(lines[4]) == 0
    assert part1(lines[5]) == 0
    assert part1(lines[6]) == 0
    assert part1(lines[7]) == 0
    assert part1(lines[8]) == 292


def test_part2():
    lines = test_input.split("\n")
    assert part2(lines[0]) == 190
    assert part2(lines[1]) == 3267
    assert part2(lines[2]) == 0
    assert part2(lines[3]) == 156
    assert part2(lines[4]) == 7290
    assert part2(lines[5]) == 0
    assert part2(lines[6]) == 192
    assert part2(lines[7]) == 0
    assert part2(lines[8]) == 292