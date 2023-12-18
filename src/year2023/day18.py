# Problem statement: https://adventofcode.com/2023/day/18

from util.inputs import movechars_dr_dc

day_title = "Lavaduct Lagoon"

example_input = """
R 6 (#70c710)
D 5 (#0dc571)
L 2 (#5713f0)
D 2 (#d2c081)
R 2 (#59c680)
D 2 (#411b91)
L 5 (#8ceee2)
U 2 (#caa173)
L 1 (#1b58a2)
U 2 (#caa171)
R 2 (#7807d2)
U 3 (#a77fa3)
L 2 (#015232)
U 2 (#7a21e3)
""".strip()

directions_U = {"U": "^", "D": "v", "L": "<", "R": ">"}
directions_0 = {"3": "^", "1": "v", "2": "<", "0": ">"}


def parse_line_1(line):
    direction, amount, _ = line.split()
    amount = int(amount)
    movechar = directions_U[direction]
    dr, dc = movechars_dr_dc[movechar]
    return dr, dc, amount


def parse_line_2(line):
    *_, color = line.split()
    color = color[2:-1]
    amount = int(color[:-1], 16)
    movechar = directions_0[color[-1]]
    dr, dc = movechars_dr_dc[movechar]
    return dr, dc, amount


# left in for historical reasons =D
def part1_floodfill(text_input: str):
    r, c = 1, 1
    dug = set(((r, c),))
    for line in text_input.split("\n"):
        dr, dc, amount = parse_line_1(line)
        for _ in range(amount):
            r += dr
            c += dc
            dug.add((r, c))

    Rmin = min(r for r, c in dug) - 1
    Rmax = max(r for r, c in dug) + 1
    Cmin = min(c for r, c in dug) - 1
    Cmax = max(c for r, c in dug) + 1

    origin = (Rmin, Cmin)
    outside = set()
    check = set((origin,))
    while len(check) > 0:
        r0, c0 = check.pop()
        outside.add((r0, c0))
        for direction in "<>^v":
            dr, dc = movechars_dr_dc[direction]
            r = r0 + dr
            c = c0 + dc
            if (r, c) in dug or (r, c) in outside:
                continue
            if r < Rmin or r > Rmax or c < Cmin or c > Cmax:
                continue
            check.add((r, c))
    return (Rmax - Rmin + 1) * (Cmax - Cmin + 1) - len(outside)


def get_area(points):
    # shoelace formula for area
    # used this reference: https://web.archive.org/web/20100405070507/http://valis.cs.uiuc.edu/~sariel/research/CG/compgeom/msg00831.html
    area = 0
    # track perimeter too because the trench is thick
    # but the area algo assumes zero-width border
    perimeter = 0
    for i in range(len(points)):
        ra, ca = points[i]
        rb, cb = points[(i + 1) % len(points)]
        perimeter += abs(ra - rb) + abs(ca - cb)
        area += ca * rb - ra * cb
    area = abs(area) // 2 + perimeter // 2 + 1
    return area


def part1(text_input: str):
    r, c = (0, 0)
    points = [(r, c)]
    for line in text_input.split("\n"):
        dr, dc, amount = parse_line_1(line)
        r += dr * amount
        c += dc * amount
        points.append((r, c))
    return get_area(points)


def part2(text_input):
    r, c = 0, 0
    points = [(r, c)]
    for line in text_input.split("\n"):
        dr, dc, amount = parse_line_2(line)
        r += dr * amount
        c += dc * amount
        points.append((r, c))
    area = get_area(points)
    return area


def test_part1():
    assert part1(example_input) == 62
    assert part1(example_input) == part1_floodfill(example_input)


def test_part2():
    assert part2(example_input) == 952408144115
