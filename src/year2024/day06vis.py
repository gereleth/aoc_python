# Problem statement: https://adventofcode.com/2024/day/6

from math import ceil
import random
from py5 import Sketch, Py5Font, PI
from aocd import get_data
import numpy as np
from functools import cache
from .day06 import day_title, test_input, GuardGallivant
from collections import deque

# print(Py5Font.list()) # list available fonts

WIDTH = 1920
HEIGHT = 1080
PADDING = 36

SILVER = (153, 153, 204)
GOLD = (230, 230, 94)
TEXT_COLOR = (204, 204, 204)
BACKGROUND = (15, 15, 35)
BACKGROUND_2 = (25, 25, 55)
WHITE = (255, 255, 255)

FONT_SIZE = 30
LEADING = FONT_SIZE
directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
angles = [0, PI / 2, PI, 3 * PI / 2]


class VisData:
    def __init__(self, text):
        self.started = False
        self.guard = GuardGallivant(text)
        self.lines = text.split("\n")
        self.R = len(self.lines)
        self.C = len(self.lines[0])
        idx = text.index("^")
        self.r0 = idx // (self.C + 1)
        self.c0 = idx % (self.C + 1)
        self.d = 0
        self.walls = [
            (r, c)
            for r in range(self.R)
            for c in range(self.C)
            if self.lines[r][c] == "#"
        ]
        self.guard_position = (self.r0, self.c0)
        self.guard_next_position = self.guard_position
        self.next_d = self.d

        self.visited = set()
        self.total_1 = 0
        self.trace = deque()
        self.trace_buffer = []
        self.part2_total = 0
        self.part2_step = -1
        self.obstruction = None
        self.total_2 = 0
        self.path_lines = None
        self.is_loop = False
        self.path_length = 0

        self.stage = "init"
        self.frame = 0
        self.done = 0.0

        self.time = 0
        self.time_per_frame = 1

    def next_frame(self):
        if not self.started:
            return
        for _ in range(int(self.time_per_frame)):
            self.time += 1
            self.tick()
            if self.stage == "out_of_bounds":
                break

    def tick(self):
        if self.stage == "init":
            self.stage = "start_step"
            self.time = 0
            self.tick()
        elif self.stage == "start_step":
            self.time_per_frame = 2 + len(data.visited) / 100
            r0, c0 = self.guard_position
            if r0 < 0 or r0 >= self.R or c0 < 0 or c0 >= self.C:
                # went out of bounds already
                self.stage = "out_of_bounds"
                self.guard_next_position = self.guard_position
                self.next_d = self.d
                self.time = 0
                self.tick()
                return
            if len(self.trace) == 0 or self.trace[-1] != (r0, c0):
                self.trace.append((r0, c0))
            if len(self.trace) >= 200:
                self.trace_buffer.append(self.trace.popleft())
            self.visited.add((r0, c0))
            self.total_1 = len(self.visited)
            dr, dc = directions[self.d]
            r, c = r0 + dr, c0 + dc
            if (r, c) in self.walls:
                self.stage = "turn"
                self.guard_next_position = self.guard_position
                self.next_d = (self.d + 1) % 4
                self.tick()
            else:
                self.guard_next_position = (r, c)
                self.next_d = self.d
                self.stage = "walk"
                self.tick()
        elif self.stage == "walk":
            duration = 10
            self.done = self.time / duration
            if self.time >= duration:
                self.time -= duration
                self.guard_position = self.guard_next_position
                self.stage = "start_step"
                self.tick()
        elif self.stage == "turn":
            duration = 10
            self.done = self.time / duration
            if self.time >= duration:
                self.time -= duration
                self.d = self.next_d
                self.stage = "start_step"
                self.tick()
        elif self.stage == "out_of_bounds":
            self.time_per_frame = 1
            duration = 180
            self.done = self.time / duration
            if len(data.trace) > 0:
                data.trace_buffer.append(data.trace.popleft())
            if self.time >= duration:
                data.trace_buffer.extend(data.trace)
                data.trace.clear()
                self.time -= duration
                self.visited.remove((self.guard.r0, self.guard.c0))
                self.guard_position = (self.guard.r0, self.guard.c0)
                self.guard_next_position = self.guard_position
                self.d = 0
                self.next_d = 0
                self.stage = "part2_start"
                self.time = 0
                self.tick()
        elif self.stage == "part2_start":
            duration = 60
            rows = ceil(self.R / duration)
            self.trace_buffer.extend(
                (r, c)
                for (r, c) in self.visited
                if ((r >= self.time * rows) and (r < (self.time + 1) * rows))
            )
            if self.time >= duration:
                self.time -= duration
                self.d = self.next_d
                self.stage = "part2_start_step"
                self.part2_step = 0
                self.obstruction = self.visited.pop()
                self.tick()
        elif self.stage == "part2_start_step":
            # appear the obstruction wall
            duration = 30
            self.done = self.time / duration
            if self.time >= duration:
                self.time -= duration
                self.collect_path()
                self.stage = "part2_show_path"
                self.tick()
        elif self.stage == "part2_show_path":
            # path appears
            duration = 120
            self.done = min(1.0, self.time / 30)
            if self.time >= duration:
                self.time -= duration
                self.stage = "part2_show_result"
                if self.is_loop:
                    self.total_2 += 1
                self.trace_buffer.append(self.obstruction)
                self.tick()
        elif self.stage == "part2_show_result":
            # shrink obstruction, paint golden dot on bg if loop
            duration = 30
            self.done = self.time / duration
            if self.time >= duration:
                self.time -= duration
                self.part2_step += 1
                if self.part2_step >= 10:
                    self.obstruction = self.visited.pop()
                    self.stage = "part2_fastforward"
                else:
                    self.obstruction = self.visited.pop()
                    self.stage = "part2_start_step"
                self.tick()
        elif self.stage == "part2_fastforward":
            if self.obstruction is None:
                return
            for _ in range(5):
                self.collect_path()
                if self.is_loop:
                    self.total_2 += 1
                self.trace_buffer.append((self.obstruction, self.is_loop))
                if len(self.visited) > 0:
                    self.obstruction = self.visited.pop()
                else:
                    self.obstruction = None
                    break

    def x(self, c):
        if self.C % 2 == 0:
            x = WIDTH // 2 - W * (self.C // 2) + W * (c + 0.5)
        else:
            x = WIDTH // 2 + W * (c - self.C // 2)
        return x

    def y(self, r):
        if self.R % 2 == 0:
            y = HEIGHT // 2 - W * (self.R // 2) + W * (r + 0.5)
        else:
            y = HEIGHT // 2 + W * (r - self.R // 2)
        return y

    def collect_path(self):
        guard = self.guard
        initial = guard.r0, guard.c0, guard.direction
        guard.obstruction = self.obstruction
        seen = set()
        self.is_loop = False
        path = [(guard.r0, guard.c0)]
        while True:
            _, _, r, c, direction, finished = guard.walk()
            state = (r, c, direction)
            path.append((r, c))
            if finished:
                # make path go out of bounds a little
                r0, c0 = path[-2]
                r += 2 if r > r0 else -2 if r < r0 else 0
                c += 2 if c > c0 else -2 if c < c0 else 0
                path[-1] = (r, c)
                break
            if state in seen:
                self.is_loop = True
                break
            seen.add(state)
        guard.r0, guard.c0, guard.direction = initial
        self.path_lines = [(self.x(c), self.y(r)) for r, c in path]
        # self.path_length = sum(
        #     abs(x1 - x2) + abs(y1 - y2)
        #     for (x1, y1), (x2, y2) in zip(path[:-1], path[1:])
        # )


text = get_data(year=2024, day=6, block=True)
data = VisData(text)
W = min((WIDTH - PADDING) // data.C, (HEIGHT - PADDING) // data.R)

background = None


class VisSketch(Sketch):
    def settings(self):
        self.size(WIDTH, HEIGHT)
        self.smooth()

    def setup(self):
        self.window_title(f"Advent of Code 2024 - Day 6 - {day_title}")

        # prepare and measure font
        font = self.create_font("Liberation Mono", FONT_SIZE)
        self.text_font(font)
        self.text_leading(LEADING)

        self.rect_mode(self.CENTER)
        self.text_align(self.RIGHT, self.CENTER)

        global background
        background = self.create_graphics(WIDTH, HEIGHT)
        background.begin_draw()
        background.rect_mode(self.CENTER)
        background.background(*BACKGROUND)
        self.draw_walls(graphics=background)
        background.end_draw()

    def mouse_clicked(self):
        data.started = True

    def draw_wall(self, r, c, graphics=None):
        g = graphics if graphics else self
        g.push()
        g.fill(*TEXT_COLOR, 128)
        g.no_stroke()
        g.rect(data.x(c), data.y(r), W, W)
        g.pop()

    def draw_walls(self, graphics=None):
        g = graphics if graphics else self
        g.push()
        g.fill(*BACKGROUND_2)
        g.stroke(*TEXT_COLOR, 128)
        g.rect(WIDTH // 2, HEIGHT // 2, W * data.C + 2, W * data.R + 2)
        for r, c in data.walls:
            self.draw_wall(r, c, graphics=graphics)
        g.pop()

    def draw_guard(self):
        self.push()
        r1, c1 = data.guard_position
        r2, c2 = data.guard_next_position
        r = r1 * (1 - data.done) + r2 * data.done
        c = c1 * (1 - data.done) + c2 * data.done
        x, y = data.x(c), data.y(r)
        self.stroke_weight(3)
        self.stroke(*SILVER)
        self.fill(*SILVER)
        a1 = angles[data.d]
        a2 = angles[data.next_d]
        if data.next_d == 0 and data.stage == "turn":
            a2 = 2 * PI
        a = a1 * (1 - data.done) + a2 * data.done
        self.translate(x, y)
        self.rotate(a)
        self.triangle(0, -W / 2, -W / 2, W / 2, W / 2, W / 2)
        self.pop()

    def draw_total_1(self):
        self.push()
        self.fill(*SILVER)
        self.text_align(self.LEFT)
        self.text(f"Visited: {data.total_1}", 100, 100)
        self.pop()

    def draw_total_2(self):
        self.push()
        self.fill(*GOLD)
        self.text_align(self.RIGHT)
        self.text(f"Loops: {data.total_2}", WIDTH - 100, 100)
        self.pop()

    def draw_trace(self):
        self.push()
        self.no_stroke()
        n = len(data.trace)
        f = min(128, n)
        for i, (r, c) in enumerate(data.trace):
            alpha = 255 - f + max(0, f + i - n)
            self.fill(*SILVER, alpha)
            self.circle(data.x(c), data.y(r), W / 2)
        self.pop()

    def draw_obstruction(self, size=1.0, alpha=1.0):
        self.push()
        self.no_stroke()
        w = size * W
        self.fill(*GOLD, int(255 * alpha))
        r, c = data.obstruction
        self.rect(data.x(c), data.y(r), w, w)
        self.pop()

    def draw_path(self, done=1.0):
        self.push()
        self.stroke(*(GOLD if data.is_loop else TEXT_COLOR), 255 * done)
        self.stroke_weight(3)
        self.shape_mode(self.LINES)
        self.no_fill()
        self.begin_shape()
        for x, y in data.path_lines:
            self.vertex(x, y)
        self.end_shape()
        self.pop()

    def draw_trace_bg(self):
        if len(data.trace_buffer) == 0:
            return
        if data.stage == "part2_start":
            background.begin_draw()
            background.smooth()
            background.no_stroke()
            for r, c in data.trace_buffer:
                background.fill(*BACKGROUND_2)
                background.rect(data.x(c), data.y(r), W - 2, W - 2)
                background.fill(*GOLD, 128)
                background.circle(data.x(c), data.y(r), W / 2)
            data.trace_buffer.clear()
            background.end_draw()
        elif data.stage == "part2_show_result":
            background.begin_draw()
            background.smooth()
            background.no_stroke()
            for r, c in data.trace_buffer:
                background.fill(*BACKGROUND_2)
                background.rect(data.x(c), data.y(r), W - 2, W - 2)
                if data.is_loop:
                    background.fill(*GOLD)
                    background.circle(data.x(c), data.y(r), W / 2)
            data.trace_buffer.clear()
            background.end_draw()
        elif data.stage == "part2_fastforward":
            background.begin_draw()
            background.smooth()
            background.no_stroke()
            for (r, c), is_loop in data.trace_buffer:
                background.fill(*BACKGROUND_2)
                background.rect(data.x(c), data.y(r), W - 2, W - 2)
                if is_loop:
                    background.fill(*GOLD)
                    background.circle(data.x(c), data.y(r), W / 2)
            data.trace_buffer.clear()
            background.end_draw()
        else:
            background.begin_draw()
            background.smooth()
            background.no_stroke()
            background.fill(*SILVER, 128)
            for r, c in data.trace_buffer:
                background.circle(data.x(c), data.y(r), W / 2)
            data.trace_buffer.clear()
            background.end_draw()

    def draw(self):
        data.next_frame()

        self.draw_trace_bg()

        self.image(background, 0, 0)

        self.draw_total_1()
        self.draw_total_2()

        if data.stage in ("init", "walk", "turn", "out_of_bounds"):
            self.draw_guard()
            self.draw_trace()
        elif data.stage == "part2_start":
            self.draw_guard()
        elif data.stage == "part2_start_step":
            self.draw_obstruction(size=4 - 3 * data.done)
            self.draw_guard()
        elif data.stage == "part2_show_path":
            self.draw_obstruction()
            self.draw_path(done=data.done)
            self.draw_guard()
        elif data.stage == "part2_show_result":
            self.draw_path(done=1 - data.done)
            self.draw_obstruction(
                size=4 - 3 * data.done, alpha=1.0 if data.is_loop else 1 - data.done
            )
            self.draw_guard()
        elif data.stage == "part2_fastforward":
            self.draw_guard()
