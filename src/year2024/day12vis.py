# Problem statement: https://adventofcode.com/2024/day/9

from py5 import Sketch  # , Py5Font
from aocd import get_data, data
from .day12 import day_title, test_input, Farm, GardenRegion
from statemachine import StateMachine, State
from dataclasses import dataclass, field
from matplotlib import colormaps
import random
from typing import List, Set
from collections import Counter
import numpy as np
from collections import defaultdict

# print(Py5Font.list()) # list available fonts
colormap_bright = colormaps.get("viridis")
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


text = data  # aocd magic, gets correct input by inspecting filepath for year/day
farm = Farm(text)
farm.collect_regions()

# prepare some data for visualisations
# contours
# flood-fill sequences


def iter_consecutives(ys):
    first = None
    for i, el in enumerate(ys):
        if first is None:
            first = el
        if i + 1 >= len(ys) or ys[i + 1] - ys[i] > 1:
            yield (first, el)
            first = None


def make_contours(region):
    # using doubled coords so borders are still ints
    doubled = set((2 * r, 2 * c) for r, c in region.plots)

    # collect perimeter parts in correct orientations
    # the region is always on the right side when looking
    # along the perimeter
    # need a list to deal with self-touching corners
    perimeter_parts = defaultdict(list)
    for r, c in doubled:
        for dr, dc in Farm.DIRECTIONS:
            if (r + 2 * dr, c + 2 * dc) not in doubled:
                if dc == 1:
                    perimeter_parts[(r - 1, c + 1)].append((r + 1, c + 1))
                elif dc == -1:
                    perimeter_parts[(r + 1, c - 1)].append((r - 1, c - 1))
                elif dr == 1:
                    perimeter_parts[(r + 1, c + 1)].append((r + 1, c - 1))
                elif dr == -1:
                    perimeter_parts[(r - 1, c - 1)].append((r - 1, c + 1))

    contours = []
    while len(perimeter_parts) > 0:
        double_keys = [key for key, value in perimeter_parts.items() if len(value) > 1]
        if len(double_keys) > 0:
            one = double_keys[0]
            two = perimeter_parts[one].pop()
        else:
            one, twos = perimeter_parts.popitem()
            two = twos[0]
        contour = [one, two]
        while contour[-1] in perimeter_parts:
            nexts = perimeter_parts.pop(contour[-1])
            if len(nexts) > 1:
                (r1, c1), (r2, c2) = contour[-2], contour[-1]
                # need to turn right, vector product sign something
                v1 = (r2 - r1, c2 - c1)
                v2 = (nexts[0][0] - r1, nexts[0][1] - c1)
                z = v1[0] * v2[1] - v1[1] * v2[0]
                if z < 0:
                    next_step = nexts[0]
                else:
                    next_step = nexts[1]
                nexts.remove(next_step)
                perimeter_parts[contour[-1]] = nexts
            else:
                next_step = nexts.pop()
            contour.append(next_step)
        contours.append(contour)

    # undouble back
    contours = [[(r / 2, c / 2) for (r, c) in contour] for contour in contours]
    return contours


def flood_fill_sequence(region):
    r0, c0 = min(region.plots)
    exploring = set([(r0, c0)])
    generations = {}
    while len(exploring) > 0:
        r, c = exploring.pop()
        generations[(r, c)] = len(generations)
        for dr, dc in Farm.DIRECTIONS:
            tile = (r + dr, c + dc)
            if tile in generations or tile in exploring or tile not in region.plots:
                continue
            exploring.add(tile)
    return generations


# farm.regions[0].contours = make_contours(farm.regions[0])
for region in farm.regions:
    region.contours = make_contours(region)
    region.flood_sequence = flood_fill_sequence(region)


class VisMachine(StateMachine):
    # data fields
    started = False
    ticks = 0
    duration = 0
    done = 1.0
    total_1 = 0
    total_2 = 0
    is_finished = False

    # animation stages

    init = State(initial=True)

    # finish animation
    end = State(final=True)

    next = init.to(end, cond="is_finished")

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
W = min((HEIGHT - 20) // farm.R, (WIDTH - 20) // farm.C)
PW = (WIDTH - farm.C * W) // 2
PH = (HEIGHT - farm.R * W) // 2
W = 50
NCOLORS = 26  # len(farm.regions)
background = None


class VisSketch(Sketch):
    def settings(self):
        self.size(WIDTH, HEIGHT)
        self.smooth()

    def setup(self):
        global background
        self.window_title(f"Advent of Code 2024 - Day 12 - {day_title}")

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
            PW + W * (farm.C - 1) / 2,
            PH + W * (farm.R - 1) / 2,
            (farm.C + 1) * W,
            (farm.R + 1) * W,
        )
        background.stroke(*BACKGROUND_2)
        for i, region in enumerate(farm.regions):
            n = ord(region.letter) - 65
            for r, c in region.plots:
                self.draw_tile(r, c, n, gr=background)
        background.end_draw()

        data.add_listener(self)

    def mouse_clicked(self):
        # data.started = not data.started
        self.save_frame(f"image{self.frame_count:03d}.png")

    def map_color(self, n, bright=False):
        colormap = colormap_bright if bright else colormap_gray
        limits = (0.2, 0.9) if bright else (0.3, 0.6)
        r, g, b, _ = colormap(self.lerp(*limits, n / NCOLORS))
        return (int(255 * r), int(255 * g), int(255 * b))

    def draw_tile(self, r, c, height, bright=True, gr=None):
        g = self if gr is None else gr
        g.push()
        # g.stroke(*BACKGROUND_2)
        g.no_stroke()
        g.fill(*self.map_color(height, bright=bright))
        y = PH + W * (r - 105)
        x = PW + W * (c - 60)
        g.rect(x, y, W, W)
        # g.fill(*BACKGROUND_2)
        # g.text_size(16)
        # g.text_align(self.CENTER, self.CENTER)
        # g.text(f"{r},{c}", x, y)
        g.pop()

    def draw(self):
        if self.frame_count == 1:
            print([i for i, r in enumerate(farm.regions) if (110, 70) in r.plots])
        self.image(background, 0, 0)
        self.shape_mode(self.LINES)
        self.no_fill()
        self.stroke(*BACKGROUND)
        self.stroke_weight(3)
        for region in farm.regions[495:496]:
            # if len(region.contours) > 1:
            for contour in region.contours:
                self.stroke_weight(3)
                for r, c in contour:
                    self.circle(PW + W * (c - 60), PH + W * (r - 105), 5)
                self.begin_shape()
                for r, c in contour:
                    self.vertex(PW + W * (c - 60), PH + W * (r - 105))
                self.end_shape()
                fat1 = (self.frame_count // 5) % len(contour)
                fat2 = (fat1 + 1) % len(contour)
                fat3 = (fat1 + 2) % len(contour)
                fat4 = (fat1 + 3) % len(contour)
                r1, c1 = contour[fat4]
                r2, c2 = contour[fat3]
                r3, c3 = contour[fat2]
                r4, c4 = contour[fat1]
                self.stroke_weight(8)
                self.line(
                    PW + W * (c1 - 60),
                    PH + W * (r1 - 105),
                    PW + W * (c2 - 60),
                    PH + W * (r2 - 105),
                )
                self.stroke_weight(6)
                self.line(
                    PW + W * (c2 - 60),
                    PH + W * (r2 - 105),
                    PW + W * (c3 - 60),
                    PH + W * (r3 - 105),
                )
                self.stroke_weight(4)
                self.line(
                    PW + W * (c3 - 60),
                    PH + W * (r3 - 105),
                    PW + W * (c4 - 60),
                    PH + W * (r4 - 105),
                )
            self.no_stroke()
            t = (self.frame_count) % (max(region.flood_sequence.values()) + 5)
            for (r, c), gen in region.flood_sequence.items():
                alpha = max(0, 250 - 250 * (t - gen - 4))
                self.fill(*WHITE, alpha)
                self.rect(PW + W * (c - 60), PH + W * (r - 105), W, W)
        data.tick()
