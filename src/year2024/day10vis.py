# Problem statement: https://adventofcode.com/2024/day/9

from py5 import Sketch  # , Py5Font
from aocd import get_data
from .day10 import day_title, test_input, HikingMap
from statemachine import StateMachine, State
from dataclasses import dataclass, field
from matplotlib import colormaps
import random
from typing import List, Set
from collections import Counter
import numpy as np
import py5_tools

# print(Py5Font.list()) # list available fonts
colormap_bright = colormaps.get("plasma")
colormap_gray = colormaps.get("gray")

WIDTH = 1920
HEIGHT = 1080
PADDING = 36

SILVER = (153, 153, 204)
GOLD = (230, 230, 94)
TEXT_COLOR = (204, 204, 204)
BACKGROUND = (15, 15, 35)
BACKGROUND_2 = (25, 25, 55)
WHITE = (255, 255, 255)

FONT_SIZE = 16
LEADING = FONT_SIZE


text = get_data(year=2024, day=10, block=True)
hiking = HikingMap(text)


@dataclass
class Trailhead:
    r: int
    c: int
    done: bool = False
    trails: List = field(default_factory=list)
    score_1: int = 0
    score_2: int = 0
    summits: Set = field(default_factory=set)


class VisMachine(StateMachine):
    # data fields
    started = False
    ticks = 0
    duration = 0
    done = 1.0
    total_1 = 0
    total_2 = 0
    trails_per_step = 1
    headpoints = [(r, c) for (r, c, h) in hiking.iter_points() if h == 0]
    random.shuffle(headpoints)
    exploring_trailheads: List[Trailhead] = []
    finished_trailheads = []
    done_exploring = False

    # animation stages

    init = State(initial=True)

    # show trailheads - red flags appear
    show_trailheads = State()
    next = init.to(show_trailheads)

    def on_enter_show_trailheads(self):
        self.duration = 120

    # start processing a few trailheads
    start_exploring = State()

    next |= show_trailheads.to(start_exploring)

    def on_enter_start_exploring(self):
        self.duration = 0

        for _ in range(min(self.trails_per_step, len(self.headpoints))):
            r, c = self.headpoints.pop()
            headpoint = Trailhead(r, c, done=False)
            headpoint.trails = [[(r, c, 0)]]
            self.exploring_trailheads.append(headpoint)
        self.trails_per_step = min(self.trails_per_step + 1, 10)

    # explore trails from current trailhead
    explore_trails = State()
    next |= start_exploring.to(explore_trails)
    next |= explore_trails.to.itself(unless="done_exploring")

    def on_enter_explore_trails(self):
        self.duration = 10
        self.done_exploring = True
        for trailhead in self.exploring_trailheads:
            trailhead.done = True
            new_trails = []
            for trail in trailhead.trails:
                r, c, h = trail[-1]
                if h == 9:
                    new_trails.append(trail)
                    continue
                trailhead.done = False
                self.done_exploring = False
                for rn, cn, hn in hiking.iter_neighbours(r, c):
                    if hn - h != 1:
                        continue
                    new_trails.append([*trail, (rn, cn, hn)])
            trailhead.trails = new_trails
            if trailhead.done:
                trailhead.score_1 = len(set(trail[-1] for trail in trailhead.trails))
                trailhead.score_2 = len(trailhead.trails)

    # show summits
    show_summits = State()
    next |= explore_trails.to(show_summits, cond="done_exploring")

    def on_enter_show_summits(self):
        self.duration = 30
        for trailhead in self.exploring_trailheads:
            trailhead.summits = set(trail[-1] for trail in trailhead.trails)
            trailhead.score_1 = len(trailhead.summits)
            trailhead.score_2 = len(trailhead.trails)

    def on_exit_show_summits(self):
        self.total_1 += sum(h.score_1 for h in self.exploring_trailheads)
        self.total_2 += sum(h.score_2 for h in self.exploring_trailheads)
        self.finished_trailheads.extend(self.exploring_trailheads)
        self.exploring_trailheads.clear()

    def is_finished(self):
        return len(self.headpoints) == 0

    next |= show_summits.to(start_exploring, unless="is_finished")

    # finish animation
    end = State(final=True)

    next |= show_summits.to(end, cond="is_finished")

    # timer to change stages
    def tick(self):
        if not self.started:
            return
        self.ticks += 1
        if self.ticks >= self.duration and not self.current_state.final:
            self.ticks = 0
            self.done = 0.0
            self.next()
        elif self.duration > 0:
            self.done = self.ticks / self.duration


data = VisMachine()
W = min((HEIGHT - 20) // hiking.R, (WIDTH - 20) // hiking.C)
PW = (WIDTH - hiking.C * W) // 2
PH = (HEIGHT - hiking.R * W) // 2
NCOLORS = 10
background = None


# z = [[int(i) for i in line] for line in hiking.lines]
# x = PW + W * np.arange(hiking.C)
# y = PH + W * np.arange(hiking.R)
# from contourpy import contour_generator

# cont_gen = contour_generator(z=z, x=x, y=y)
# contours = {}
# for h in range(1, 18):
#     contours[h] = cont_gen.lines(h / 2)


class VisSketch(Sketch):
    def settings(self):
        self.size(WIDTH, HEIGHT)
        self.smooth()

    def setup(self):
        global background
        self.window_title(f"Advent of Code 2024 - Day 10 - {day_title}")

        # prepare and measure font
        font = self.create_font("Liberation Mono", FONT_SIZE)
        self.text_font(font)
        self.text_leading(LEADING)

        self.rect_mode(self.CENTER)
        self.text_align(self.CENTER, self.CENTER)

        background = self.create_graphics(WIDTH, HEIGHT)
        background.begin_draw()
        background.rect_mode(self.CENTER)
        background.background(*BACKGROUND)
        background.fill(*BACKGROUND_2)
        background.stroke(*TEXT_COLOR)
        background.rect(
            PW + W * (hiking.C - 1) / 2,
            PH + W * (hiking.R - 1) / 2,
            (hiking.C + 1) * W,
            (hiking.R + 1) * W,
        )
        background.stroke(*BACKGROUND_2)
        for r, c, height in hiking.iter_points():
            self.draw_tile(r, c, height, gr=background)
        # self.draw_contours(gr=background)
        background.end_draw()

        data.add_listener(self)

    def mouse_clicked(self):
        data.started = not data.started
        self.save_frame(f"image{self.frame_count:03d}.png")

    def map_color(self, n, bright=False):
        colormap = colormap_bright if bright else colormap_gray
        limits = (0.2, 0.9) if bright else (0.3, 0.6)
        r, g, b, _ = colormap(self.lerp(*limits, n / NCOLORS))
        return (int(255 * r), int(255 * g), int(255 * b))

    def draw_tile(self, r, c, height, bright=False, gr=None):
        g = self if gr is None else gr
        g.push()
        g.stroke(*BACKGROUND_2)
        g.fill(*self.map_color(height, bright=bright))
        y = PH + W * r
        x = PW + W * c
        g.rect(x, y, W, W)
        g.pop()

    def draw_headpoint_circle(self, r, c, big=False):
        self.push()
        self.translate(PW + W * c, PH + W * r)
        self.fill(*WHITE)
        self.no_stroke()
        self.circle(0, 0, W / 2 if big else W / 4)
        self.pop()

    def draw_headpoint_flag(self, r, c, done=False):
        self.push()
        self.translate(PW + W * c, PH + W * r)
        x1 = -W / 4
        x2 = W * 0.4
        y1 = -W * 1.25
        y2 = -W * 0.75
        color = SILVER
        self.stroke_weight(3)
        self.stroke(*BACKGROUND_2, 128)
        self.line(x1 + 1, y1 + 1, x1 + 1, 2 * y2 - y1 + 1)
        self.stroke(*color)
        self.line(x1, y1, x1, 2 * y2 - y1)
        color = GOLD if done else WHITE
        self.stroke(*BACKGROUND_2, 128)
        self.stroke_weight(1)
        self.fill(*color)
        self.triangle(x1, y1, x1, y2, x2, (y1 + y2) * 0.5)
        self.pop()

    def draw_headpoints(self):
        if data.current_state == VisMachine.init:
            return
        if data.current_state == VisMachine.show_trailheads:
            done = (hiking.R + hiking.C) * data.done
            for r, c in data.headpoints:
                if r + c < done:
                    self.draw_headpoint_circle(r, c)
        else:
            for r, c in data.headpoints:
                self.draw_headpoint_circle(r, c)
            for head in data.exploring_trailheads:
                if data.current_state == VisMachine.show_summits:
                    self.draw_headpoint_flag(head.r, head.c, done=True)
                    self.draw_headpoint_circle(head.r, head.c, True)
                else:
                    self.draw_headpoint_circle(head.r, head.c, True)
            for head in data.finished_trailheads:
                self.draw_headpoint_flag(head.r, head.c, done=True)

    def draw_summits(self):
        if data.current_state == VisMachine.show_summits:
            done = self.constrain(data.done * 2, 0, 1)
            size = self.lerp(3, 0.5, done)
            summits = set(
                point for head in data.exploring_trailheads for point in head.summits
            )
            self.push()
            self.fill(*SILVER, int(255 * done))
            self.no_stroke()
            for r, c, _ in summits:
                x, y = PW + W * c, PH + W * r
                self.circle(x, y, W * size)
            self.pop()

    def draw_trail_tiles(self):
        active = set(
            point
            for head in data.exploring_trailheads
            for trail in head.trails
            for point in trail
        )
        for r, c, h in active:
            self.draw_tile(r, c, h, bright=True)

    def draw_trail_lines(self):
        self.push()
        self.shape_mode(self.LINES)
        self.no_fill()
        self.stroke(*GOLD)
        self.stroke_weight(2)
        for head in data.exploring_trailheads:
            trails = head.trails
            destinations = Counter(trail[-1] for trail in trails)
            angles = {d: self.PI * 2 / n for d, n in destinations.items()}
            for i, trail in enumerate(trails):
                d = trail[-1]
                destinations[d] -= 1
                n = destinations[d]
                if n <= 1:
                    dxi, dyi = 0, 0
                else:
                    ai = angles[d] / 2 + angles[d] * n
                    dxi, dyi = W * 0.25 * self.cos(ai), W * 0.25 * self.sin(ai)
                if trail[-1][-1] == 9:
                    self.stroke(*GOLD)
                else:
                    self.stroke("white")
                self.begin_shape()
                for r, c, _ in trail:
                    self.vertex(PW + W * c + dxi, PH + W * r + dyi)
                self.end_shape()
        self.pop()

    def draw_totals(self):
        self.push()
        x0 = 200
        y0 = PH - 0.5 * W + 30
        self.fill(*SILVER)
        self.text_align(self.RIGHT, self.BASELINE)
        self.text_size(30)
        self.text("Part 1: ", x0, y0)
        self.text_align(self.LEFT, self.BASELINE)
        if data.current_state != VisMachine.show_summits:
            text = f"{data.total_1}"
        else:
            text = (
                f"{data.total_1} + {sum(h.score_1 for h in data.exploring_trailheads)}"
            )
        self.text(text, x0, y0)
        self.fill(*GOLD)
        self.text_align(self.RIGHT, self.BASELINE)
        self.text_size(30)
        self.text("Part 2: ", x0, y0 + 60)
        self.text_align(self.LEFT, self.BASELINE)
        if data.current_state != VisMachine.show_summits:
            text = f"{data.total_2}"
        else:
            text = (
                f"{data.total_2} + {sum(h.score_2 for h in data.exploring_trailheads)}"
            )
        self.text(text, x0, y0 + 60)
        self.pop()

    # def draw_contours(self, gr=None):
    #     g = self if gr is None else gr
    #     g.push()
    #     g.shape_mode(self.LINE_LOOP)
    #     g.no_fill()
    #     g.stroke_weight(2)
    #     for h, lines in contours.items():
    #         color = self.map_color(h, bright=True)
    #         g.stroke(*color)
    #         for line in lines:
    #             g.begin_shape()
    #             g.vertices(line)
    #             g.end_shape()
    #     g.pop()

    def draw(self):
        self.image(background, 0, 0)
        data.tick()
        # self.draw_contours()
        self.draw_trail_tiles()
        self.draw_headpoints()
        self.draw_trail_lines()
        self.draw_summits()
        self.draw_totals()
