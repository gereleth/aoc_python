# Problem statement: https://adventofcode.com/2024/day/16

import heapq
from collections import namedtuple
from math import inf
from typing import Iterator

day_title = "Reindeer Maze"

State = namedtuple("State", ["cost", "r", "c", "direction", "path"])


def parse_input(text_input: str):
    lines = text_input.split("\n")
    return lines


class ReindeerMaze:
    DIRECTIONS = [(1, 0), (0, 1), (-1, 0), (0, -1)]

    def __init__(self, text: str):
        self.lines = text.split("\n")
        self.R, self.C = len(self.lines), len(self.lines[0])
        start = text.index("S")
        self.r0 = start // (self.C + 1)
        self.c0 = start % (self.C + 1)
        finish = text.index("E")
        self.finish = (finish // (self.C + 1), finish % (self.C + 1))
        self.direction = 1
        self.lowest_cost_to_position = {}

    def can_go_to(self, r: int, c: int) -> bool:
        if r >= self.R or r < 0 or c >= self.C or c < 0:
            return False
        if self.lines[r][c] == "#":
            return False
        return True

    def next_states(self, state: State) -> Iterator[State]:
        # Go straight ahead until a wall or finish point
        # At every location with a possible turn left of right yield turned state
        # Skip states leading to already visited positions (if cost before was cheaper)
        r, c, direction = state.r, state.c, state.direction
        left = (direction + 1) % 4
        right = (direction - 1) % 4
        path = []
        while True:
            # look left, look right
            for d in [left, right]:
                dr, dc = self.DIRECTIONS[d]
                if not self.can_go_to(r + dr, c + dc):
                    continue
                position = (r + dr, c + dc, d)
                cost = state.cost + len(path) + 1001
                cost_before = self.lowest_cost_to_position.get(position, inf)
                if cost > cost_before:
                    continue
                self.lowest_cost_to_position[position] = cost
                yield State(
                    cost,
                    *position,
                    state.path + path + [(r + dr, c + dc)],
                )
            # go straight unless a wall or finish point
            dr, dc = self.DIRECTIONS[direction]
            if not self.can_go_to(r + dr, c + dc):
                break
            r += dr
            c += dc
            path.append((r, c))
            if (r, c) == self.finish:
                yield State(state.cost + len(path), r, c, direction, state.path + path)
                break

    def min_cost_to_finish(self, state: State) -> int:
        # If the maze had no walls the cost to finish would be this
        r0, c0, direction = state.r, state.c, state.direction
        r, c = self.finish
        dr, dc = self.DIRECTIONS[direction]
        delta_r, delta_c = r - r0, c - c0
        if delta_r == 0 and delta_c == 0:
            return 0
        elif delta_r == 0:
            return abs(delta_c) + (2000 if dc * delta_c < 0 else 0)
        elif delta_c == 0:
            return abs(delta_r) + (2000 if dr * delta_r < 0 else 0)
        else:
            # this is specific to finish being in top right corner
            return abs(delta_r) + abs(delta_c) + (2000 if direction in (0, 3) else 1000)

    def search(self, yield_search_states=False):
        start_state = State(0, self.r0, self.c0, self.direction, [(self.r0, self.c0)])
        queue = [(0, start_state)]
        beststates = []
        bestcost = inf
        iteration = 0
        while len(queue) > 0:
            iteration += 1
            priority, previous_state = heapq.heappop(queue)
            # if iteration % 1000 == 0:
            #     print(
            #         "best",
            #         bestcost,
            #         "iter",
            #         iteration,
            #         "prio",
            #         priority,
            #         "queue",
            #         len(queue),
            #         "cost",
            #         previous_state.cost,
            #         "path",
            #         len(previous_state.path),
            #         previous_state.path[-3:],
            #     )
            lower_bound = previous_state.cost + self.min_cost_to_finish(previous_state)
            if lower_bound > bestcost:
                continue
            if yield_search_states:
                yield previous_state, priority, bestcost, len(queue)
            for state in self.next_states(previous_state):
                if (state.r, state.c) == self.finish:
                    if state.cost < bestcost:
                        bestcost = state.cost
                        beststates = [state]
                        if yield_search_states:
                            yield state, state.cost, bestcost, len(queue)
                    elif state.cost == bestcost:
                        if yield_search_states:
                            yield state, state.cost, bestcost, len(queue)
                        beststates.append(state)
                else:
                    dist = self.min_cost_to_finish(state)
                    lower_bound = state.cost + dist
                    if lower_bound > bestcost:
                        continue
                    priority = lower_bound
                    heapq.heappush(queue, (priority, state))
        yield beststates, bestcost, bestcost, 0

    def get_best_cost(self):
        _, bestcost, *_ = next(self.search())
        return bestcost

    def get_best_tiles_count(self):
        beststates, *_ = next(self.search())
        return len(set(pos for state in beststates for pos in state.path))


def part1(text_input: str) -> int:
    maze = ReindeerMaze(text_input)
    return maze.get_best_cost()


def part2(text_input: str) -> int:
    maze = ReindeerMaze(text_input)
    return maze.get_best_tiles_count()


test_input = """
###############
#.......#....E#
#.#.###.#.###.#
#.....#.#...#.#
#.###.#####.#.#
#.#.#.......#.#
#.#.#####.###.#
#...........#.#
###.#.#####.#.#
#...#.....#.#.#
#.#.#.###.#.#.#
#.....#...#.#.#
#.###.#.#.#.#.#
#S..#.....#...#
###############
""".strip()

test_input_2 = """
#################
#...#...#...#..E#
#.#.#.#.#.#.#.#.#
#.#.#.#...#...#.#
#.#.#.#.###.#.#.#
#...#.#.#.....#.#
#.#.#.#.#.#####.#
#.#...#.#.#.....#
#.#.#####.#.###.#
#.#.#.......#...#
#.#.###.#####.###
#.#.#...#.....#.#
#.#.#.#####.###.#
#.#.#.........#.#
#.#.#.#########.#
#S#.............#
#################
""".strip()


def test_next_states_1():
    maze = ReindeerMaze(test_input)
    state = State(0, maze.r0, maze.c0, maze.direction, [(maze.r0, maze.c0)])
    next_states = list(maze.next_states(state))
    assert next_states == [
        State(cost=1001, r=12, c=1, direction=2, path=[(13, 1), (12, 1)])
    ]


def test_next_states_2():
    maze = ReindeerMaze(test_input)
    state = State(cost=1001, r=12, c=1, direction=2, path=[(13, 1), (12, 1)])
    next_states = list(maze.next_states(state))
    assert next_states == [
        State(
            cost=2003, r=11, c=2, direction=1, path=[(13, 1), (12, 1), (11, 1), (11, 2)]
        ),
        State(
            cost=2005,
            r=9,
            c=2,
            direction=1,
            path=[(13, 1), (12, 1), (11, 1), (10, 1), (9, 1), (9, 2)],
        ),
    ]


def test_part1():
    assert part1(test_input) == 7036
    assert part1(test_input_2) == 11048


def test_part2():
    assert part2(test_input) == 45
    assert part2(test_input_2) == 64
