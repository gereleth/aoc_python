# Problem statement: https://adventofcode.com/2025/day/6

day_title = "Trash Compactor"


def part1(text_input: str) -> int:
    lines = [line.split() for line in text_input.split("\n")]
    problems = [[line[i] for line in lines] for i in range(len(lines[0]))]
    total = 0
    for problem in problems:
        sign = problem.pop()
        if sign == "+":
            total += sum(int(p) for p in problem)
        elif sign == "*":
            product = 1
            for p in problem:
                product *= int(p)
            total += product
    return total


def part2(text_input: str) -> int:
    lines = text_input.split("\n")
    R, C = len(lines), len(lines[0])
    total = 0
    numbers = []
    for c in range(C - 1, -1, -1):
        number = "".join(lines[r][c] for r in range(R - 1)).strip()
        if number:
            numbers.append(int(number))
        sign = lines[R - 1][c]
        if sign == "+":
            total += sum(numbers)
            numbers.clear()
        elif sign == "*":
            product = 1
            for n in numbers:
                product *= n
            total += product
            numbers.clear()
    return total


test_input = """
123 328  51 64 
 45 64  387 23 
  6 98  215 314
*   +   *   +  
""".strip("\n")


def test_part1():
    assert part1(test_input) == 4277556


def test_part2():
    assert part2(test_input) == 3263827
