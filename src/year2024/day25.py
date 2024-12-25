# Problem statement: https://adventofcode.com/2024/day/25

day_title = "Code Chronicle"


def parse_input(text_input: str):
    lines = text_input.split("\n")
    return lines


def part1(text_input: str) -> int:
    keys = []
    locks = []
    for item in text_input.split("\n\n"):
        is_lock = item.startswith("#####")
        item = item.split()
        H, W = len(item), len(item[0])
        heights = [sum(item[j][i] == "#" for j in range(H)) - 1 for i in range(W)]
        if is_lock:
            locks.append(heights)
        else:
            keys.append(heights)
    fit = 0
    for key in keys:
        for lock in locks:
            fit += all(hk + hl <= H - 2 for hk, hl in zip(key, lock))
    return fit


def part2(text_input: str) -> int:
    return 0


test_input = """
#####
.####
.####
.####
.#.#.
.#...
.....

#####
##.##
.#.##
...##
...#.
...#.
.....

.....
#....
#....
#...#
#.#.#
#.###
#####

.....
.....
#.#..
###..
###.#
###.#
#####

.....
.....
.....
#....
#.#..
#.#.#
#####
""".strip()


def test_part1():
    assert part1(test_input) == 3
