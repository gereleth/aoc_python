# Problem statement: https://adventofcode.com/2023/day/22

from collections import defaultdict
from dataclasses import dataclass

day_title = "Sand Slabs"

example_input_1 = """
1,0,1~1,2,1
0,0,2~2,0,2
0,2,3~2,2,3
0,0,4~0,2,4
2,0,5~2,2,5
0,1,6~2,1,6
1,1,8~1,1,9
""".strip()


@dataclass
class Brick:
    x0: int
    y0: int
    z0: int
    x1: int
    y1: int
    z1: int

    def __str__(self):
        return f"{self.x0},{self.y0},{self.z0}~{self.x1},{self.y1},{self.z1}"

    def top_cubes(self):
        for x in range(self.x0, self.x1 + 1):
            for y in range(self.y0, self.y1 + 1):
                yield x, y, self.z1

    def cubes_below(self):
        zmin = self.z0 - 1
        for x in range(self.x0, self.x1 + 1):
            for y in range(self.y0, self.y1 + 1):
                yield x, y, zmin


def parse_brick(line):
    c0, c1 = line.split("~")
    x0, y0, z0 = map(int, c0.split(","))
    x1, y1, z1 = map(int, c1.split(","))
    return Brick(x0, y0, z0, x1, y1, z1)


def fall_down(bricks):
    bricks.sort(key=lambda x: x.z0)
    on_ground = set()
    for brick in bricks:
        if brick.z0 == 1:
            # this block fell down
            on_ground.update(brick.top_cubes())
            continue
        falling = True
        while falling:
            for cube in brick.cubes_below():
                if cube[2] == 0 or cube in on_ground:
                    falling = False
            if not falling:
                break
            brick.z0 -= 1
            brick.z1 -= 1
        on_ground.update(brick.top_cubes())
    return bricks


def part1(text_input: str):
    bricks = [parse_brick(line) for line in text_input.split("\n")]
    bricks = fall_down(bricks)

    cube_to_brick = {}
    for i, brick in enumerate(bricks):
        cube_to_brick.update({cube: i for cube in brick.top_cubes()})

    is_supported_by = defaultdict(set)
    supports = defaultdict(set)
    for i, brick in enumerate(bricks):
        for cube in brick.cubes_below():
            if cube in cube_to_brick:
                other = cube_to_brick[cube]
                is_supported_by[i].add(other)
                supports[other].add(i)

    can_disintegrate = 0

    have_multiple_supports = set()
    for brick_above, bricks_below in is_supported_by.items():
        if len(bricks_below) > 1:
            have_multiple_supports.add(brick_above)

    for i, _ in enumerate(bricks):
        if i not in supports:
            can_disintegrate += 1
            continue
        if len(supports[i] - have_multiple_supports) == 0:
            can_disintegrate += 1
    return can_disintegrate


def part2(text_input: str):
    # start the same as part 1
    bricks = [parse_brick(line) for line in text_input.split("\n")]
    bricks = fall_down(bricks)

    cube_to_brick = {}
    for i, brick in enumerate(bricks):
        cube_to_brick.update({cube: i for cube in brick.top_cubes()})

    is_supported_by = defaultdict(set)
    supports = defaultdict(set)
    for i, brick in enumerate(bricks):
        for cube in brick.cubes_below():
            if cube in cube_to_brick:
                other = cube_to_brick[cube]
                is_supported_by[i].add(other)
                supports[other].add(i)

    total = 0
    for i, brick in enumerate(bricks):
        if i not in supports:
            # can't cause a cascade if nothing is on top
            continue
        might_fall = set(supports[i])
        fell = set((i,))
        smth_fell = True
        while smth_fell:
            smth_fell = False
            new_falls = set()
            for j in might_fall:
                if len(is_supported_by[j] - fell) == 0:
                    new_falls.add(j)
            if len(new_falls) > 0:
                smth_fell = True
                might_fall -= new_falls
                for j in new_falls:
                    might_fall.update(supports[j])
                fell.update(new_falls)
        total_fell = len(fell) - 1
        total += total_fell
    return total


def test_part1():
    assert part1(example_input_1) == 5


def test_part2():
    assert part2(example_input_1) == 7
