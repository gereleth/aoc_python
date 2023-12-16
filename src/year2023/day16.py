# Problem statement: https://adventofcode.com/2023/day/16

from util.inputs import movechars_dr_dc

day_title = "The Floor Will Be Lava"

example_input = r"""
.|...\....
|.-.\.....
.....|-...
........|.
..........
.........\
..../.\\..
.-.-/..|..
.|....-|.\
..//.|....
""".strip()


direction_transforms = {
    "\\": {">": "v", "v": ">", "<": "^", "^": "<"},
    "/": {">": "^", "v": "<", "<": "v", "^": ">"},
    ".": {">": ">", "v": "v", "<": "<", "^": "^"},
    "|": {">": "^v", "v": "v", "<": "^v", "^": "^"},
    "-": {">": ">", "v": "<>", "<": "<", "^": "<>"},
}


def part1(text_input):
    origin = tuple((0, -1, ">"))
    lines = text_input.split("\n")
    energized = count_energized_tiles(lines, origin)
    return energized


def count_energized_tiles(lines, origin):
    processed = set()
    origins = set((origin,))
    energized = set()
    while len(origins) > 0:
        origin = origins.pop()
        processed.add(origin)
        r0, c0, direction = origin
        energized.add((r0, c0))
        dr, dc = movechars_dr_dc[direction]
        r = r0 + dr
        c = c0 + dc
        if r < 0 or r >= len(lines) or c < 0 or c >= len(lines[0]):
            continue
        newchar = lines[r][c]
        newdirs = direction_transforms[newchar][direction]
        for newdir in newdirs:
            neworigin = tuple((r, c, newdir))
            if neworigin not in processed:
                origins.add(neworigin)
    return len(energized) - 1


def part2(text_input):
    best = 0
    lines = text_input.split("\n")
    R = len(lines)
    C = len(lines[0])
    origins = (
        [tuple((-1, c, "v")) for c in range(0, C)]
        + [tuple((R, c, "^")) for c in range(0, C)]
        + [tuple((r, -1, ">")) for r in range(0, R)]
        + [tuple((r, C, "<")) for r in range(0, R)]
    )
    for origin in origins:
        cnt = count_energized_tiles(lines, origin)
        if cnt > best:
            best = cnt
    return best


def test_part1():
    assert part1(example_input) == 46


def test_part2():
    assert part2(example_input) == 51
