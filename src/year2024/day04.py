# Problem statement: https://adventofcode.com/2024/day/4

day_title = "Ceres Search"


def part1(text_input: str) -> int:
    lines = text_input.split("\n")
    R, C = len(lines), len(lines[0])
    xmas = 0
    wanted = ("XMAS", "SAMX")
    steps = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for r in range(R):
        for c in range(C):
            for dr, dc in steps:
                if (
                    r + 3 * dr < 0
                    or r + 3 * dr >= R
                    or c + 3 * dc < 0
                    or c + 3 * dc >= C
                ):
                    continue
                word = "".join(lines[r + i * dr][c + i * dc] for i in range(4))
                xmas += word in wanted
    return xmas


def part2(text_input: str) -> int:
    lines = text_input.split("\n")
    R, C = len(lines), len(lines[0])
    xmas = 0
    wanted = ("MAS", "SAM")
    diagonal_1 = ((-1, -1), (0, 0), (1, 1))
    diagonal_2 = ((1, -1), (0, 0), (-1, 1))
    for r in range(1, R - 1):
        for c in range(1, C - 1):
            if lines[r][c] != "A":
                continue
            word_1 = "".join(lines[r + dr][c + dc] for dr, dc in diagonal_1)
            word_2 = "".join(lines[r + dr][c + dc] for dr, dc in diagonal_2)
            if word_1 in wanted and word_2 in wanted:
                xmas += 1
    return xmas


test_input = """
MMMSXXMASM
MSAMXMSMSA
AMXSXMAAMM
MSAMASMSMX
XMASAMXAMM
XXAMMXXAMA
SMSMSASXSS
SAXAMASAAA
MAMMMXMMMM
MXMXAXMASX
""".strip()

test_input_2 = """

""".strip()


def test_part1():
    assert part1(test_input) == 18


def test_part2():
    assert part2(test_input) == 9
