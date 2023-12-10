# Problem statement: https://adventofcode.com/2023/day/10

from util.inputs import movechars_dr_dc

day_title = "Pipe Maze"

example_input_1 = """
.....
.S-7.
.|.|.
.L-J.
.....
""".strip()

example_input_2 = """
7-F7-
.FJ|7
SJLL7
|F--J
LJ.LJ
""".strip()


example_input_3 = """
...........
.S-------7.
.|F-----7|.
.||.....||.
.||.....||.
.|L-7.F-J|.
.|..|.|..|.
.L--J.L--J.
...........
""".strip()


example_input_4 = """
FF7FSF7F7F7F7F7F---7
L|LJ||||||||||||F--J
FL-7LJLJ||||||LJL-77
F--JF--7||LJLJ7F7FJ-
L---JF-JLJ.||-FJLJJ7
|F|F-JF---7F7-L7L|7|
|FFJF7L7F-JF7|JL---7
7-L-JL7||F7|L7F-7F7|
L.L7LFJ|||||FJL7||LJ
L7JLJL-JLJLJL--JLJ.L
""".strip()


directions = {
    "-": "<>",
    "|": "^v",
    "F": "v>",
    "J": "<^",
    "L": "^>",
    "7": "v<",
    "S": "v>^<",
    ".": "",
}
opposite = {">": "<", "<": ">", "^": "v", "v": "^"}


def locate_main_loop(pipes):
    R = len(pipes)
    C = len(pipes[0])
    start = "".join(pipes).index("S")
    r_start = start // C
    c_start = start % C
    loop = [(r_start, c_start)]

    def connects(r, c, direction):
        dr, dc = movechars_dr_dc[dir]
        neighbour_r = r + dr
        neighbour_c = c + dc
        if neighbour_r >= R or neighbour_r < 0:
            return False, None
        if neighbour_c >= C or neighbour_c < 0:
            return False, None
        neighbour = pipes[neighbour_r][neighbour_c]

        if opposite[direction] in directions[neighbour]:
            return True, (neighbour_r, neighbour_c)
        return False, None

    discarded = set()

    while not (loop[-1] == (r_start, c_start) and len(loop) > 1):
        came_from = None if len(loop) <= 1 else loop[-2]
        r, c = loop[-1]
        symbol = pipes[r][c]
        symbol_dirs = directions[symbol]
        for dir in symbol_dirs:
            connected, neighbour_pos = connects(r, c, dir)
            if (
                neighbour_pos == came_from
                or not connected
                or neighbour_pos in discarded
            ):
                continue
            loop.append(neighbour_pos)
            break
        if loop[-1] == (r, c):
            # we could not go anywhere
            discarded.add((r, c))
            loop.pop()
    return loop


def part1(text_input: str):
    pipes = text_input.split("\n")
    loop = locate_main_loop(pipes)
    return (len(loop) - 1) // 2


def test_part_1():
    assert part1(example_input_1) == 4
    assert part1(example_input_2) == 8


def part2(text_input: str):
    pipes = text_input.split("\n")
    loop = locate_main_loop(pipes)
    # first find out which pipe type is at the S point
    sr, sc = loop[0]
    neighbour1 = loop[1]
    neighbour2 = loop[-2]
    sdirections = ""
    for nr, nc in [neighbour1, neighbour2]:
        if sr == nr:
            sdirections += ">" if nc > sc else "<"
        else:
            sdirections += "v" if nr > sr else "^"
    s_symbol = next(
        char for char, dirs in directions.items() if sorted(dirs) == sorted(sdirections)
    )
    pipes[sr] = pipes[sr].replace("S", s_symbol)
    # make loop a set for faster "point in loop" checks
    loop = set(loop)
    # scan the maze line by line
    # we begin line scan outside the loop
    # every time we cross a vertical loop piece
    # (it could be a "|" or a "L7" or a "F--J" for example)
    # we switch between outside and inside
    # "F--7", "L--J" type things don't cause a switch
    enclosed = 0
    for r, line in enumerate(pipes):
        out = True
        verticals = set()
        for c, char in enumerate(line):
            if (r, c) in loop:
                verticals.update(directions[char])
                if "v" in verticals and "^" in verticals:
                    out = not out
                    verticals.clear()
                elif ">" not in directions[char]:
                    verticals.clear()
            elif not out:
                enclosed += 1
    return enclosed


def test_part_2():
    assert part2(example_input_3) == 4
    assert part2(example_input_4) == 10
