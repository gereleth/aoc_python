# Problem statement: https://adventofcode.com/2024/day/18

from collections import namedtuple
import heapq
from typing import Iterator
from math import inf, isinf

day_title = "RAM Run"
State = namedtuple("State", ["cost", "r", "c"])


class MemoryRegion:
    DIRECTIONS = [(1, 0), (0, 1), (-1, 0), (0, -1)]

    def __init__(self, text: str, finish=(70, 70), nwalls=1024):
        self.R, self.C = finish[0] + 1, finish[1] + 1
        self.r0 = 0
        self.c0 = 0
        self.finish = finish
        self.walls = set()
        for line in text.split()[:nwalls]:
            a, b = line.split(",")
            self.walls.add((int(a), int(b)))
        self.lowest_cost_to_position = {}

    def can_go_to(self, r: int, c: int) -> bool:
        if r >= self.R or r < 0 or c >= self.C or c < 0:
            return False
        if (r, c) in self.walls:
            return False
        return True

    def next_states(self, state: State) -> Iterator[State]:
        r, c = state.r, state.c
        for dr, dc in self.DIRECTIONS:
            if not self.can_go_to(r + dr, c + dc):
                continue
            position = (r + dr, c + dc)
            cost = state.cost + 1
            cost_before = self.lowest_cost_to_position.get(position, inf)
            if cost >= cost_before:
                continue
            self.lowest_cost_to_position[position] = cost
            yield State(cost, *position)

    def min_cost_to_finish(self, state: State) -> int:
        # ignore the obstacles
        return abs(self.finish[0] - state.r) + abs(self.finish[1] - state.c)

    def search(self, yield_search_states=False):
        start_state = State(0, self.r0, self.c0)
        queue = [(0, start_state)]
        bestcost = inf
        beststate = None
        iteration = 0
        while len(queue) > 0:
            iteration += 1
            priority, previous_state = heapq.heappop(queue)
            lower_bound = previous_state.cost + self.min_cost_to_finish(previous_state)
            if lower_bound > bestcost:
                continue
            if yield_search_states:
                yield previous_state, priority, bestcost, len(queue)
            for state in self.next_states(previous_state):
                if (state.r, state.c) == self.finish:
                    if state.cost < bestcost:
                        bestcost = state.cost
                        beststate = state
                        if yield_search_states:
                            yield state, state.cost, bestcost, len(queue)
                else:
                    dist = self.min_cost_to_finish(state)
                    lower_bound = state.cost + dist
                    if lower_bound >= bestcost:
                        continue
                    priority = lower_bound
                    heapq.heappush(queue, (priority, state))
        yield beststate, bestcost, bestcost, 0

    def get_best_cost(self):
        _, bestcost, *_ = next(self.search())
        return bestcost


def part1(text_input: str) -> int:
    region = MemoryRegion(text_input)
    res = region.get_best_cost()
    return res


def part2(text_input: str) -> int:
    lines = text_input.split()
    a = 0
    b = len(lines) - 1
    while a < b:
        m = (a + b) // 2
        region = MemoryRegion(text_input, nwalls=m)
        cost = region.get_best_cost()
        if isinf(cost):
            b = m
        else:
            a = m + 1
    return lines[a - 1]


test_input = """
5,4
4,2
4,5
3,0
2,1
6,3
2,4
1,5
0,6
3,3
2,6
5,1
1,2
5,5
2,5
6,5
1,4
0,4
6,4
1,1
6,1
1,0
0,5
1,6
2,0
""".strip()

# I wish the grid sizes were part of the input...


def test_part1():
    region = MemoryRegion(test_input, finish=(6, 6), nwalls=12)
    res = region.get_best_cost()
    assert res == 22


def test_part2():
    lines = test_input.split()
    a = 0
    b = len(lines) - 1
    while a < b:
        m = (a + b) // 2
        region = MemoryRegion(test_input, finish=(6, 6), nwalls=m)
        cost = region.get_best_cost()
        if isinf(cost):
            b = m
        else:
            a = m + 1
    assert lines[a - 1] == "6,1"
