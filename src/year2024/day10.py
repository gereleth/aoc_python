# Problem statement: https://adventofcode.com/2024/day/10

day_title = "Hoof It"


# really need to implement some base class that does all these things
class HikingMap:
    DIRECTIONS = [(-1, 0), (0, 1), (1, 0), (0, -1)]

    def __init__(self, text):
        self.lines = text.split("\n")
        self.R, self.C = len(self.lines), len(self.lines[0])

    def iter_points(self):
        for r, line in enumerate(self.lines):
            for c, char in enumerate(line):
                yield r, c, int(char)

    def iter_neighbours(self, r, c):
        for dr, dc in self.DIRECTIONS:
            if r + dr >= self.R or r + dr < 0 or c + dc >= self.C or c + dc < 0:
                continue
            next_height = int(self.lines[r + dr][c + dc])
            yield (r + dr, c + dc, next_height)

    def collect_trails(self, r0, c0):
        if self.lines[r0][c0] != "0":
            raise ValueError("Not a valid trail starting point")
        trails = [[(r0, c0, 0)]]
        done = set()
        while len(trails) > 0:
            trail = trails.pop()
            r, c, height = trail[-1]
            for rn, cn, hn in self.iter_neighbours(r, c):
                if hn != height + 1:
                    continue
                new_trail = [*trail, (rn, cn, hn)]
                if hn == 9:
                    done.add(tuple(new_trail))
                else:
                    trails.append(new_trail)
        return done

    def trailhead_score(self, r, c):
        trails = self.collect_trails(r, c)
        return len(set(t[-1] for t in trails))

    def trailhead_rating(self, r, c):
        trails = self.collect_trails(r, c)
        return len(trails)


def part1(text_input: str) -> int:
    hiking = HikingMap(text_input)
    score = 0
    for r, c, height in hiking.iter_points():
        if height == 0:
            score += hiking.trailhead_score(r, c)
    return score


def part2(text_input: str) -> int:
    hiking = HikingMap(text_input)
    rating = 0
    for r, c, height in hiking.iter_points():
        if height == 0:
            rating += hiking.trailhead_rating(r, c)
    return rating


test_input = """
89010123
78121874
87430965
96549874
45678903
32019012
01329801
10456732
""".strip()

test_input_2 = """

""".strip()


def test_part1():
    assert part1(test_input) == 36


def test_part2():
    assert part2(test_input) == 81
