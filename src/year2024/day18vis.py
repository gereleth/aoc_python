# Problem statement: https://adventofcode.com/2024/day/18

from py5 import Sketch  # , Py5Font
from aocd import data
from .day18 import day_title
from statemachine import StateMachine, State
from matplotlib import colormaps
from math import inf
import heapq
from collections import namedtuple
from typing import Iterator

# print(Py5Font.list()) # list available fonts
colormap_bright = colormaps.get("viridis")

WIDTH = 1920
HEIGHT = 1080
PADDING = 36

SILVER = (153, 153, 204)
GOLD = (230, 230, 94)
TEXT_COLOR = (204, 204, 204)
BACKGROUND = (15, 15, 35)
BACKGROUND_2 = (25, 25, 55)
WHITE = (255, 255, 255)
WALL_COLOR = (200, 200, 200)
WALL_COLOR_2 = (107, 107, 128)
FONT_SIZE = 30

text = data  # aocd magic, gets correct input by inspecting filepath for year/day

# could have imported this from day18 but I want to collect best paths here
# so I copy-pasted instead
SearchState = namedtuple("SearchState", ["cost", "r", "c", "path"])


class MemoryRegion:
    DIRECTIONS = [(1, 0), (0, 1), (-1, 0), (0, -1)]

    def __init__(self, text: str, finish=(70, 70), nwalls=1024):
        self.R, self.C = finish[0] + 1, finish[1] + 1
        self.r0 = 0
        self.c0 = 0
        self.finish = finish
        self.nwalls = nwalls
        self.walls = []
        for line in text.split():
            a, b = line.split(",")
            self.walls.append((int(a), int(b)))
        self.active_walls = set(self.walls[:nwalls])
        self.lowest_cost_to_position = {}

    def set_walls(self, n: int):
        self.nwalls = n
        self.active_walls = set(self.walls[:n])
        self.lowest_cost_to_position.clear()

    def can_go_to(self, r: int, c: int) -> bool:
        if r >= self.R or r < 0 or c >= self.C or c < 0:
            return False
        if (r, c) in self.active_walls:
            return False
        return True

    def next_states(self, state: SearchState) -> Iterator[SearchState]:
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
            yield SearchState(cost, *position, state.path + [position])

    def min_cost_to_finish(self, state: SearchState) -> int:
        # ignore the obstacles
        return abs(self.finish[0] - state.r) + abs(self.finish[1] - state.c)

    def search(self, yield_search_states=False):
        start_state = SearchState(0, self.r0, self.c0, [(self.r0, self.c0)])
        queue = [(0, start_state)]
        bestcost = inf
        beststate = None
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

    def get_best_path(self):
        beststate, bestcost, *_ = next(self.search())
        return beststate.path if beststate else []


def diff_paths(old_path, new_path):
    # split paths into 4 parts:
    # path1 = start to divergence
    # out = old path from divergence to convergence
    # in = new path from divergence to convergence
    # path2 = convergence to end
    for i, (old, new) in enumerate(zip(old_path, new_path)):
        if old != new:
            break
    for j, (old, new) in enumerate(zip(old_path[::-1], new_path[::-1])):
        if old != new:
            break
    path1 = old_path[:i]
    path2 = old_path[-j:]
    path_out = old_path[i - 1 : len(old_path) - j + 1]
    path_in = new_path[i - 1 : len(new_path) - j + 1]
    return path1, path2, path_in, path_out


class VisMachine(StateMachine):
    # data fields
    started = False
    ticks = 0
    duration = 0
    done = 1.0
    total_1 = 0
    total_2 = 0
    is_finished = False
    # animation data
    maze = MemoryRegion(text)
    path1 = maze.get_best_path()
    path2 = []
    path_out = []
    path_in = []
    nwalls = 0
    path_tiles = set(path1)
    walls_in = {}
    golden_block = None
    path_blocked = False
    done_falling = False
    bad_walls = set()
    # animation stages

    init = State(initial=True)

    rocks_fall = State()
    transition = init.to(rocks_fall)

    def on_enter_rocks_fall(self):
        self.duration = 1
        for _ in range(10):
            wall = self.maze.walls[self.nwalls]
            self.walls_in[wall] = 9
            self.nwalls += 1
            if self.nwalls >= self.maze.nwalls:
                self.done_falling = True
                break

    reveal_path = State()

    def on_enter_reveal_path(self):
        self.duration = 90

    transition |= rocks_fall.to.itself(unless="done_falling") | rocks_fall.to(
        reveal_path
    )

    more_rocks = State()
    transition |= reveal_path.to(more_rocks)

    def on_enter_more_rocks(self):
        self.duration = 1
        for _ in range(5):
            wall = self.maze.walls[self.nwalls]
            self.nwalls += 1
            self.walls_in[wall] = 10
            if wall in self.path_tiles:
                self.path_blocked = True
                self.maze.set_walls(self.nwalls)
                self.bad_walls.add(wall)
                break

    rebuild_path = State()

    def on_enter_rebuild_path(self):
        self.duration = 60
        old_path = self.path1 + self.path_in[1:-1] + self.path2
        new_path = self.maze.get_best_path()
        if len(new_path) > 0:
            self.path_blocked = False
            self.path1, self.path2, self.path_in, self.path_out = diff_paths(
                old_path, new_path
            )
            self.path_tiles.difference_update(self.path_out)
            self.path_tiles.update(self.path_in)
        else:
            self.golden_block = self.maze.walls[self.nwalls - 1]
            idx = old_path.index(self.golden_block)
            self.path1 = old_path[:idx]
            self.path2 = old_path[idx + 1 :]
            self.path_in = []
            self.path_out = old_path[idx - 1 : idx + 1]

    show_golden_block = State()

    def on_enter_show_golden_block(self):
        self.duration = 60

    transition |= (
        more_rocks.to.itself(unless="path_blocked")
        | more_rocks.to(rebuild_path, cond="path_blocked")
        | rebuild_path.to(more_rocks, cond="not path_blocked")
        | rebuild_path.to(show_golden_block, cond="path_blocked")
    )

    # finish animation
    end = State(final=True)
    transition |= show_golden_block.to(end)

    # timer to change stages
    def tick(self):
        if not self.started:
            return
        self.ticks += 1
        if self.ticks >= self.duration and not self.current_state.final:
            self.ticks = 0
            self.done = 0.0
            self.transition()
        elif self.duration > 0:
            self.done = self.ticks / self.duration


data = VisMachine()
R = data.maze.R
C = data.maze.C
W = min((HEIGHT - 20) // R, (WIDTH - 20) // C)
PW = (WIDTH - C * W) // 2
PH = (HEIGHT - R * W) // 2
background = None


class VisSketch(Sketch):
    def settings(self):
        self.size(WIDTH, HEIGHT)
        self.smooth()

    def setup(self):
        global background
        self.window_title(f"Advent of Code 2024 - Day 18 - {day_title}")

        # prepare and measure font
        font = self.create_font("Liberation Mono", FONT_SIZE)
        self.text_font(font)
        self.text_size(FONT_SIZE)

        self.rect_mode(self.CENTER)
        self.text_align(self.CENTER, self.CENTER)
        background = self.create_graphics(WIDTH, HEIGHT)
        background.begin_draw()
        self.draw_background(gr=background)
        background.end_draw()

        data.add_listener(self)

    def mouse_clicked(self):
        if data.started:
            title = "-".join(day_title.lower().split())
            self.save_frame(f"2024-day18-{title}-{self.frame_count:03d}.png")
        data.started = not data.started

    def draw_background(self, gr=None):
        g = self if gr is None else gr
        g.push()
        g.rect_mode(self.CORNER)
        g.background(*BACKGROUND)
        g.fill(*BACKGROUND_2)
        g.rect(PW - W / 2, PH - W / 2, C * W, R * W)
        g.fill(*WALL_COLOR, 32)
        g.rect(PW - W / 2, PH - W / 2, C * W, R * W)
        g.pop()

    def draw_rocks_fall(self):
        to_bg = set()
        self.push()
        self.rect_mode(self.CENTER)
        self.stroke(*BACKGROUND_2)
        for wall, ticksleft in data.walls_in.items():
            r, c = wall
            if ticksleft == 0 and not (
                data.current_state == VisMachine.rebuild_path and wall in data.bad_walls
            ):
                to_bg.add(wall)
            else:
                # alpha = 64 + 5 * ticksleft
                if wall in data.bad_walls:
                    self.fill(255, 0, 0, 128)
                else:
                    self.fill(*WALL_COLOR_2)
                size = W * (1 + ticksleft / 5)
                self.rect(PW + c * W, PH + r * W, size, size)
                data.walls_in[wall] = max(0, ticksleft - 1)
        for wall in to_bg:
            data.walls_in.pop(wall, None)
        self.draw_walls_on_bg(to_bg)
        self.pop()

    def draw_walls_on_bg(self, walls):
        background.begin_draw()
        background.push()
        background.rect_mode(self.CENTER)
        background.stroke(*BACKGROUND_2)
        for r, c in walls:
            if (r, c) in data.bad_walls:
                background.fill(255, 0, 0, 64)
            else:
                background.fill(*WALL_COLOR_2)
            background.rect(PW + c * W, PH + r * W, W, W)
        background.pop()
        background.end_draw()

    def draw_golden_block(self):
        if data.current_state == VisMachine.show_golden_block:
            self.push()
            self.rect_mode(self.CENTER)
            alpha = int(255 * data.done)
            self.fill(*GOLD, alpha)
            self.no_stroke()
            r, c = data.golden_block
            self.rect(PW + c * W, PH + r * W, W, W)
            self.pop()
        elif data.current_state == VisMachine.end:
            self.push()
            self.rect_mode(self.CENTER)
            self.fill(*GOLD)
            self.no_stroke()
            r, c = data.golden_block
            self.rect(PW + c * W, PH + r * W, W, W)
            self.pop()

    def draw_routes(self):
        if data.current_state == VisMachine.reveal_path:
            self.push()
            self.shape_mode(self.LINES)
            self.stroke_weight(W / 2)
            self.no_fill()
            self.stroke(*SILVER, int(255 * data.done))
            self.begin_shape()
            for r, c in data.path1:
                self.vertex(PW + W * c, PH + W * r)
            self.end_shape()
            self.pop()
        elif data.current_state == VisMachine.more_rocks:
            self.push()
            self.shape_mode(self.LINES)
            self.stroke_weight(W / 2)
            self.no_fill()
            self.stroke(*SILVER)
            self.begin_shape()
            for r, c in data.path1:
                self.vertex(PW + W * c, PH + W * r)
            for r, c in data.path_in[1:-1]:
                self.vertex(PW + W * c, PH + W * r)
            for r, c in data.path2:
                self.vertex(PW + W * c, PH + W * r)
            self.end_shape()
            self.pop()
        elif data.current_state == VisMachine.rebuild_path:
            self.push()
            self.shape_mode(self.LINES)
            self.no_fill()
            self.stroke(*SILVER)
            self.stroke_weight(W / 2)
            self.begin_shape()
            for r, c in data.path1:
                self.vertex(PW + W * c, PH + W * r)
            self.end_shape()
            self.begin_shape()
            for r, c in data.path2:
                self.vertex(PW + W * c, PH + W * r)
            self.end_shape()

            self.stroke_weight((1 - data.done) * W / 2)
            self.begin_shape()
            for r, c in data.path_out:
                self.vertex(PW + W * c, PH + W * r)
            self.end_shape()
            self.stroke_weight(data.done * W / 2)
            self.begin_shape()
            for r, c in data.path_in:
                self.vertex(PW + W * c, PH + W * r)
            self.end_shape()
            self.pop()
        elif data.current_state == VisMachine.show_golden_block:
            self.push()
            self.shape_mode(self.LINES)
            self.stroke_weight(W / 2)
            self.no_fill()
            self.stroke(*SILVER, 255 - int(128 * data.done))
            self.begin_shape()
            for r, c in data.path1:
                self.vertex(PW + W * c, PH + W * r)
            self.end_shape()
            self.begin_shape()
            for r, c in data.path2:
                self.vertex(PW + W * c, PH + W * r)
            self.end_shape()

            self.pop()
        elif data.current_state == VisMachine.end:
            self.push()
            self.shape_mode(self.LINES)
            self.stroke_weight(W / 2)
            self.no_fill()
            self.stroke(*SILVER, 128)
            self.begin_shape()
            for r, c in data.path1:
                self.vertex(PW + W * c, PH + W * r)
            self.end_shape()
            self.begin_shape()
            for r, c in data.path2:
                self.vertex(PW + W * c, PH + W * r)
            self.end_shape()
            self.pop()

    def draw(self):
        data.tick()
        self.image(background, 0, 0)
        self.draw_rocks_fall()
        self.draw_routes()
        self.draw_golden_block()
        # self.draw_totals()
        # if data.walls_in:
        #     background.begin_draw()
        #     self.draw_changed_walls(gr=background)
        #     background.end_draw()
