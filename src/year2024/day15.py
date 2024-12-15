# Problem statement: https://adventofcode.com/2024/day/15

from util.inputs import movechars_dr_dc

day_title = "Warehouse Woes"


class Warehouse:
    def __init__(self, text: str):
        self.lines = [list(line) for line in text.split("\n")]
        self.R, self.C = len(self.lines), len(self.lines[0])
        robot_index = text.index("@")
        self.r0, self.c0 = robot_index // (self.C + 1), robot_index % (self.C + 1)

    def maybe_move(self, movechar):
        dr, dc = movechars_dr_dc[movechar]
        moved = 0
        r, c = self.r0 + dr, self.c0 + dc
        while self.lines[r][c] == "O":
            moved += 1
            r += dr
            c += dc
        if self.lines[r][c] == "#":
            return
        while moved > 0:
            self.lines[r][c] = "O"
            r -= dr
            c -= dc
            moved -= 1
        self.lines[r][c] = "@"
        self.lines[self.r0][self.c0] = "."
        self.r0 = r
        self.c0 = c

    def calc_gps(self):
        total = 0
        for r, line in enumerate(self.lines):
            for c, char in enumerate(line):
                if char == "O":
                    total += 100 * r + c
        return total


class BigWarehouse:
    def __init__(self, text: str):
        text = (
            text.replace("#", "##")
            .replace("O", "[]")
            .replace(".", "..")
            .replace("@", "@.")
        )
        self.lines = [list(line) for line in text.split("\n")]
        self.R, self.C = len(self.lines), len(self.lines[0])
        robot_index = text.index("@")
        self.r0, self.c0 = robot_index // (self.C + 1), robot_index % (self.C + 1)

    def maybe_move_horizontal(self, movechar):
        _, dc = movechars_dr_dc[movechar]
        moved = 0
        r, c = self.r0, self.c0 + dc
        while self.lines[r][c] in "[]":
            moved += 1
            c += dc
        if self.lines[r][c] == "#":
            return
        while moved > 0:
            self.lines[r][c] = "]" if dc > 0 else "["
            c -= dc
            self.lines[r][c] = "[" if dc > 0 else "]"
            c -= dc
            moved -= 2
        self.lines[r][c] = "@"
        self.lines[self.r0][self.c0] = "."
        self.r0 = r
        self.c0 = c

    def maybe_move_vertical(self, movechar):
        dr, _ = movechars_dr_dc[movechar]
        # collect boxes to push
        offsets = [set([0])]
        r, c0 = self.r0, self.c0
        decided = False
        while not decided:
            r = r + dr
            # check for walls ahead
            for offset in offsets[-1]:
                if self.lines[r][c0 + offset] == "#":
                    return
            # check for boxes ahead
            new_offsets = set()
            for offset in offsets[-1]:
                if self.lines[r][c0 + offset] == "[":
                    new_offsets.add(offset)
                    new_offsets.add(offset + 1)
                elif self.lines[r][c0 + offset] == "]":
                    new_offsets.add(offset)
                    new_offsets.add(offset - 1)
            # no new boxes, we can move
            if len(new_offsets) == 0:
                decided = True
                break
            # else we are undecided and continue the while loop
            offsets.append(new_offsets)
        # now we move the boxes
        while len(offsets) > 1:
            todo = offsets.pop()
            for offset in sorted(todo)[::2]:
                self.lines[r][c0 + offset] = "["
                self.lines[r - dr][c0 + offset] = "."
                self.lines[r][c0 + offset + 1] = "]"
                self.lines[r - dr][c0 + offset + 1] = "."
            r -= dr
        # and now we move the robot
        self.lines[r][c0] = "@"
        self.lines[r - dr][c0] = "."
        self.r0 = r

    def maybe_move(self, movechar):
        if movechar in "^v":
            self.maybe_move_vertical(movechar)
        else:
            self.maybe_move_horizontal(movechar)

    def calc_gps(self):
        total = 0
        for r, line in enumerate(self.lines):
            for c, char in enumerate(line):
                if char == "[":
                    total += 100 * r + c
        return total

    def debug_str(self):
        return "\n".join("".join(line) for line in self.lines)


def part1(text_input: str) -> int:
    warehouse_text, instructions_text = text_input.split("\n\n")
    instructions_text = "".join(instructions_text.split())
    wh = Warehouse(warehouse_text)
    for movechar in instructions_text:
        wh.maybe_move(movechar)
    ans = wh.calc_gps()
    return ans


def part2(text_input: str) -> int:
    warehouse_text, instructions_text = text_input.split("\n\n")
    instructions_text = "".join(instructions_text.split())
    wh = BigWarehouse(warehouse_text)
    for movechar in instructions_text:
        wh.maybe_move(movechar)
    ans = wh.calc_gps()
    return ans


test_input = """
########
#..O.O.#
##@.O..#
#...O..#
#.#.O..#
#...O..#
#......#
########

<^^>>>vv<v>>v<<
""".strip()

test_input_2 = """
##########
#..O..O.O#
#......O.#
#.OO..O.O#
#..O@..O.#
#O#..O...#
#O..O..O.#
#.OO.O.OO#
#....O...#
##########

<vv>^<v^>v>^vv^v>v<>v^v<v<^vv<<<^><<><>>v<vvv<>^v^>^<<<><<v<<<v^vv^v>^
vvv<<^>^v^^><<>>><>^<<><^vv^^<>vvv<>><^^v>^>vv<>v<<<<v<^v>^<^^>>>^<v<v
><>vv>v^v^<>><>>>><^^>vv>v<^^^>>v^v^<^^>v^^>v^<^v>v<>>v^v^<v>v^^<^^vv<
<<v<^>>^^^^>>>v^<>vvv^><v<<<>^^^vv^<vvv>^>v<^^^^v<>^>vvvv><>>v^<<^^^^^
^><^><>>><>^^<<^^v>>><^<v>^<vv>>v>>>^v><>^v><<<<v>>v<v<v>vvv>^<><<>^><
^>><>^v<><^vvv<^^<><v<<<<<><^v<<<><<<^^<v<^^^><^>>^<v^><<<^>>^v<v^v<v^
>^>>^v>vv>^<<^v<>><<><<v<<v><>v<^vv<<<>^^v^>^^>>><<^v>>v^v><^^>>^<>vv^
<><^^>^^^<><vvvvv^v<v<<>^v<v>v<<^><<><<><<<^^<<<^<<>><<><^^^>^^<>^>v<>
^^>vv<^v^v<vv>^<><v<^v>^^^>>>^^vvv^>vvv<>>>^<^>>>>>^<<^v>^vvv<>^<><<v>
v^^>>><<^^<>>^v^<v^vv<>v^<<>^<^v^v><^<<<><<^<v><v<>vv>>v><v^<vv<>v^<<^
""".strip()


def test_part1():
    assert part1(test_input) == 2028
    assert part1(test_input_2) == 10092


def test_part2():
    assert part2(test_input_2) == 9021


# This is a lot of extra tests lol


def test_big_parse():
    text = """
#######
#.....#
#..O..#
#.O@.O#
#######
""".strip()
    wh = BigWarehouse(text)
    print(wh.debug_str())
    assert (
        wh.debug_str()
        == """
##############
##..........##
##....[]....##
##..[]@...[]##
##############
""".strip()
    )
    assert wh.R == 5
    assert wh.C == 14
    assert wh.r0 == 3
    assert wh.c0 == 6


def test_big_move_right():
    text = """
#####
#@O.#
#####
""".strip()
    wh = BigWarehouse(text)
    wh.maybe_move(">")
    wh.maybe_move(">")
    assert (
        wh.debug_str()
        == """
##########
##..@[].##
##########
""".strip()
    )


def test_big_move_left():
    text = """
#########
#O..OO@.#
#########
""".strip()
    wh = BigWarehouse(text)
    wh.maybe_move("<")
    print(wh.debug_str())
    assert (
        wh.debug_str()
        == """
##################
##[]...[][]@....##
##################
""".strip()
    )


def test_big_move_no_left():
    text = """
######
#OO@.#
######
""".strip()
    wh = BigWarehouse(text)
    wh.maybe_move("<")
    print(wh.debug_str())
    assert (
        wh.debug_str()
        == """
############
##[][]@...##
############
""".strip()
    )


def test_big_move_up_1():
    text = """
######
#....#
#..O.#
#..@.#
######
""".strip()
    wh = BigWarehouse(text)
    assert (
        wh.debug_str()
        == """
############
##........##
##....[]..##
##....@...##
############
""".strip()
    )
    wh.maybe_move("^")
    print(wh.debug_str())
    assert (
        wh.debug_str()
        == """
############
##....[]..##
##....@...##
##........##
############
""".strip()
    )


def test_big_move_up_2():
    text = """
######
#....#
#..O.#
#..@.#
######
""".strip()
    wh = BigWarehouse(text)
    assert (
        wh.debug_str()
        == """
############
##........##
##....[]..##
##....@...##
############
""".strip()
    )
    wh.maybe_move("^")
    wh.maybe_move("^")
    print(wh.debug_str())
    assert (
        wh.debug_str()
        == """
############
##....[]..##
##....@...##
##........##
############
""".strip()
    )


def test_big_move_up_3():
    text = """
######
#....#
#..OO#
#.@O.#
#....#
######
""".strip()
    wh = BigWarehouse(text)
    print(wh.debug_str())
    assert (
        wh.debug_str()
        == """
############
##........##
##....[][]##
##..@.[]..##
##........##
############
""".strip()
    )
    for char in ">>v>^^":
        wh.maybe_move(char)
    print(wh.debug_str())
    assert (
        wh.debug_str()
        == """
############
##....[][]##
##.....[].##
##.....@..##
##........##
############
""".strip()
    )


def test_big_move_down_1():
    text = """
######
#..@.#
#..O.#
#....#
######
""".strip()
    wh = BigWarehouse(text)
    assert (
        wh.debug_str()
        == """
############
##....@...##
##....[]..##
##........##
############
""".strip()
    )
    wh.maybe_move("v")
    print(wh.debug_str())
    assert (
        wh.debug_str()
        == """
############
##........##
##....@...##
##....[]..##
############
""".strip()
    )


def test_big_move_down_2():
    text = """
######
#..@.#
#..O.#
#....#
######
""".strip()
    wh = BigWarehouse(text)
    assert (
        wh.debug_str()
        == """
############
##....@...##
##....[]..##
##........##
############
""".strip()
    )
    wh.maybe_move(">")
    wh.maybe_move("v")
    print(wh.debug_str())
    assert (
        wh.debug_str()
        == """
############
##........##
##.....@..##
##....[]..##
############
""".strip()
    )
