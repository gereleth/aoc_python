# Problem statement: https://adventofcode.com/2023/day/17

from util.inputs import movechars_dr_dc
from collections import namedtuple
import math
import heapq


State = namedtuple("State", ["cost", "r", "c", "direction", "path"])

day_title = "Clumsy Crucible"

example_input = """
2413432311323
3215453535623
3255245654254
3446585845452
4546657867536
1438598798454
4457876987766
3637877979653
4654967986887
4564679986453
1224686865563
2546548887735
4322674655533
""".strip()

example_input_1 = """
111111111111
999999999991
999999999991
999999999991
999999999991
""".strip()


class CrucibleCity:
    def __init__(self, text_input, min_straight, max_straight):
        self.costs = [[int(char) for char in line] for line in text_input.split("\n")]
        self.R = len(self.costs)
        self.C = len(self.costs[0])
        self.start = (0, 0)
        self.min_cost = {}
        self.finish = (self.R - 1, self.C - 1)
        self.min_straight = min_straight
        self.max_straight = max_straight

    def next_states(self, state: State):
        # always turn here and explore all straight moves left/right
        r0, c0, direction = state.r, state.c, state.direction
        next_directions = "<>" if direction in "^v" else "^v"
        for next_direction in next_directions:
            dr, dc = movechars_dr_dc[next_direction]
            extra_cost = 0
            extra_path = ""
            for i in range(1, self.max_straight + 1):
                r, c = r0 + i * dr, c0 + i * dc
                if r < 0 or r >= self.R:
                    break
                if c < 0 or c >= self.C:
                    break
                extra_path += next_direction
                extra_cost += self.costs[r][c]
                if i >= self.min_straight:
                    min_cost = self.min_cost.get(
                        (r, c, next_direction in "<>"), math.inf
                    )
                    if state.cost + extra_cost >= min_cost:
                        continue
                    self.min_cost[(r, c, next_direction in "<>")] = (
                        state.cost + extra_cost
                    )
                    yield State(
                        state.cost + extra_cost,
                        r,
                        c,
                        next_direction,
                        state.path + extra_path,
                    )


def search(city: CrucibleCity, yield_search_states=False):
    queue = [(0, State(0, *city.start, ">", "")), (0, State(0, *city.start, "v", ""))]
    heapq.heapify(queue)
    beststate = None
    bestcost = math.inf
    while len(queue) > 0:
        priority, prev_state = heapq.heappop(queue)
        # print(len(queue), prev_state)
        lower_bound = (
            prev_state.cost
            + abs(prev_state.r - city.finish[0])
            + abs(prev_state.c - city.finish[1])
        )
        if lower_bound >= bestcost:
            continue
        if yield_search_states:
            yield prev_state, priority, bestcost, len(queue)
        for state in city.next_states(prev_state):
            if (state.r, state.c) == city.finish:
                if state.cost < bestcost:
                    beststate = state
                    bestcost = state.cost
                    if yield_search_states:
                        yield state, state.cost, bestcost, len(queue)
            else:
                dist = abs(state.r - city.finish[0]) + abs(state.c - city.finish[1])
                lower_bound = state.cost + dist
                if lower_bound >= bestcost:
                    continue
                priority = lower_bound
                heapq.heappush(queue, (priority, state))
    # print("search done", beststate)
    yield beststate, bestcost, bestcost, len(queue)


def part1(text_input: str):
    city = CrucibleCity(text_input, 1, 3)
    beststate, *_ = next(search(city))
    return beststate.cost


def part2(text_input):
    city = CrucibleCity(text_input, 4, 10)
    beststate, *_ = next(search(city))
    return beststate.cost


def test_part1():
    assert part1(example_input) == 102


def test_part2():
    assert part2(example_input) == 94
    assert part2(example_input_1) == 71
