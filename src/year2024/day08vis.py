# Problem statement: https://adventofcode.com/2024/day/6

from math import ceil
import random
import py5
from py5 import Sketch, Py5Font, PI
from aocd import get_data
import numpy as np
from functools import cache
from .day08 import day_title, test_input, AntennaField
from collections import deque
from statemachine import StateMachine, State

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

FONT_SIZE = 16
LEADING = FONT_SIZE


text = get_data(year=2024, day=8, block=True)


class VisMachine(StateMachine):
    # data fields
    ticks = 0
    duration = 0
    done = 1.0
    total_1 = 0
    total_2 = 0
    started = False
    data = AntennaField(text)
    R, C = data.R, data.C
    frequencies = sorted(data.antennas.keys())
    frequency_index = -1
    frequency = None
    antenna_pairs = []
    pair_index = -1
    antenna_a = None
    antenna_b = None
    silver_nodes = []
    gold_nodes = []
    silver_set = set()
    gold_set = set()
    done_frequencies = set()

    # animation stages

    init = State(initial=True)

    # show initial antennas with colored letters
    show_frequencies = State()
    next = init.to(show_frequencies)

    def on_enter_show_frequencies(self):
        self.duration = 120

    # start a single frequency
    start_frequency = State()
    next |= show_frequencies.to(start_frequency)

    def on_enter_start_frequency(self):
        self.duration = 30
        self.frequency_index += 1
        self.frequency = self.frequencies[self.frequency_index]
        self.pair_index = -1
        antennas = self.data.antennas[self.frequency]
        self.antenna_pairs = [
            (a, b) for (i, a) in enumerate(antennas[:-1]) for b in antennas[i + 1 :]
        ]

    # start a pair of antennas (show pair highlight)
    start_pair = State()
    next |= start_frequency.to(start_pair)

    def on_enter_start_pair(self):
        self.duration = 30
        self.pair_index += 1
        self.antenna_a, self.antenna_b = self.antenna_pairs[self.pair_index]

    # show line between pair of antennas
    show_line = State()
    next |= start_pair.to(show_line)

    def on_enter_show_line(self):
        self.duration = 60

    # show silver antinodes for this pair
    pair_silver = State()

    next |= show_line.to(pair_silver)

    def on_enter_pair_silver(self):
        self.duration = 40
        self.silver_nodes = self.data.find_antinodes(
            (self.antenna_a, self.antenna_b), single=True
        )

    # show gold antinodes for this pair
    pair_gold = State()

    next |= pair_silver.to(pair_gold)

    def on_enter_pair_gold(self):
        self.duration = 40
        self.gold_nodes = self.data.find_antinodes(
            (self.antenna_a, self.antenna_b), single=False
        )

    # finish showing pair
    end_pair = State()

    next |= pair_gold.to(end_pair) | end_pair.to(start_pair, cond="has_next_pair")

    def on_enter_end_pair(self):
        self.duration = 30

    def has_next_pair(self):
        return self.pair_index + 1 < len(self.antenna_pairs)

    # finish showing frequency
    end_frequency = State()

    next |= end_pair.to(end_frequency, unless="has_next_pair")

    def on_enter_end_frequency(self):
        self.duration = 10

    def on_exit_end_frequency(self):
        self.done_frequencies.add(self.frequency)

    def has_next_frequency(self):
        return self.frequency_index + 1 < len(self.frequencies)

    next |= end_frequency.to(
        start_frequency, cond="has_next_frequency and not going_fast"
    )

    # start fast frequency processing - all pairs at once

    def going_fast(self):
        return self.frequency_index >= 1

    # begin frequency fast
    start_frequency_fast = State()

    next |= end_frequency.to(
        start_frequency_fast, cond="has_next_frequency and going_fast"
    )

    def on_enter_start_frequency_fast(self):
        self.duration = 10
        self.frequency_index += 1
        self.frequency = self.frequencies[self.frequency_index]
        antennas = self.data.antennas[self.frequency]
        self.antenna_pairs = [
            (a, b) for (i, a) in enumerate(antennas[:-1]) for b in antennas[i + 1 :]
        ]

    # show lines fast
    show_lines_fast = State()

    next |= start_frequency_fast.to(show_lines_fast)

    def on_enter_show_lines_fast(self):
        self.duration = 10

    # show silver fast
    silver_fast = State()

    next |= show_lines_fast.to(silver_fast)

    def on_enter_silver_fast(self):
        self.duration = 20
        self.silver_nodes = self.data.find_antinodes(
            self.data.antennas[self.frequency], single=True
        )

    # show gold fast
    gold_fast = State()

    next |= silver_fast.to(gold_fast)

    next |= gold_fast.to(end_frequency)

    def on_enter_gold_fast(self):
        self.duration = 20
        self.gold_nodes = self.data.find_antinodes(
            self.data.antennas[self.frequency], single=False
        )

    # finish animation
    end = State(final=True)

    next |= end_frequency.to(end, unless="has_next_frequency")

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
W = min((WIDTH - PADDING) // data.C, (HEIGHT - PADDING) // data.R)

background = None


class VisSketch(Sketch):
    def settings(self):
        self.size(WIDTH, HEIGHT)
        self.smooth()

    def setup(self):
        self.window_title(f"Advent of Code 2024 - Day 8 - {day_title}")

        # prepare and measure font
        font = self.create_font("Liberation Mono", FONT_SIZE)
        self.text_font(font)
        self.text_leading(LEADING)

        self.rect_mode(self.CENTER)
        self.text_align(self.CENTER, self.CENTER)

        global background
        background = self.create_graphics(WIDTH, HEIGHT)
        background.begin_draw()
        background.rect_mode(self.CENTER)
        background.background(*BACKGROUND)
        self.draw_walls(graphics=background)
        background.end_draw()

        data.add_listener(self)

    def mouse_clicked(self):
        data.started = True

    def x(self, c):
        if data.C % 2 == 0:
            x = WIDTH // 2 - W * (data.C // 2) + W * (c + 0.5)
        else:
            x = WIDTH // 2 + W * (c - data.C // 2)
        return x

    def y(self, r):
        if data.R % 2 == 0:
            y = HEIGHT // 2 - W * (data.R // 2) + W * (r + 0.5)
        else:
            y = HEIGHT // 2 + W * (r - data.R // 2)
        return y

    def draw_walls(self, graphics=None):
        g = graphics if graphics else self
        g.push()
        g.fill(*BACKGROUND_2)
        g.stroke(*TEXT_COLOR, 128)
        g.rect(WIDTH // 2, HEIGHT // 2, W * data.C + 2, W * data.R + 2)
        g.pop()

    def show_antennas(self, saturation=0.0):
        self.push()
        n = len(data.frequencies)
        self.color_mode(self.HSB, n, 100, 100)
        for i, frequency in enumerate(data.frequencies):
            locations = data.data.antennas[frequency]
            self.fill(i, int(saturation * 80), 80)
            for r, c in locations:
                self.text(frequency, self.x(c), self.y(r))
        self.pop()

    def draw_antennas(self, done=1.0, active_frequency=None):
        self.push()
        self.no_stroke()
        n = len(data.frequencies)
        self.color_mode(self.HSB, n, 100, 100)
        for i, frequency in enumerate(data.frequencies):
            locations = data.data.antennas[frequency]
            if frequency in data.done_frequencies:
                continue
            active = frequency == active_frequency
            for r, c in locations:
                if active:
                    self.fill(i, 80, 80, int(255 * done))
                    self.circle(self.x(c), self.y(r), W)
                self.fill(i, 0, 80, 255 if active else 128)
                self.text(frequency, self.x(c), self.y(r))
        self.pop()

    def draw_pair_highlight(self, size=1.0):
        self.push()
        ra, ca = data.antenna_a
        rb, cb = data.antenna_b
        self.no_fill()
        self.stroke_weight(3)
        self.stroke(*TEXT_COLOR)
        self.circle(self.x(ca), self.y(ra), size * W)
        self.circle(self.x(cb), self.y(rb), size * W)
        self.pop()

    def draw_line(self, antenna_a, antenna_b, done=1.0):
        self.push()
        max_distance = 1.5 * (data.R + data.C) * W
        ra, ca = antenna_a
        rb, cb = antenna_b
        x0 = self.x((ca + cb) / 2)
        y0 = self.y((ra + rb) / 2)
        dx = self.x(ca) - x0
        dy = self.y(ra) - y0
        step = self.sqrt(dx**2 + dy**2)
        nsteps = (done * max_distance) / step
        self.stroke(*TEXT_COLOR)
        self.stroke_weight(1)
        xl = self.x(-0.5)
        xr = self.x(data.C - 0.5)
        yt = self.y(-0.5)
        yb = self.y(data.R - 0.5)
        steps_to_borders = []
        if ra != rb:
            steps_to_borders.extend(((yt - y0) / dy, (yb - y0) / dy))
        if ca != cb:
            steps_to_borders.extend(((xl - x0) / dx, (xr - x0) / dx))
        max_pos_steps = min(p for p in steps_to_borders if p > 0)
        max_neg_steps = min(-p for p in steps_to_borders if -p > 0)
        x1 = x0 - min(max_neg_steps, nsteps) * dx
        y1 = y0 - min(max_neg_steps, nsteps) * dy
        x2 = x0 + min(max_pos_steps, nsteps) * dx
        y2 = y0 + min(max_pos_steps, nsteps) * dy
        self.line(x1, y1, x2, y2)
        self.pop()

    def draw_silver_antinodes(self, size=1.0, alpha=1.0):
        self.push()
        self.fill(*SILVER, int(255 * alpha))
        self.no_stroke()
        for r, c in data.silver_nodes:
            self.circle(self.x(c), self.y(r), size * W)
        self.pop()

    def draw_gold_antinodes(self, size=1.0, alpha=1.0):
        self.push()
        self.fill(*GOLD, int(255 * alpha))
        self.no_stroke()
        for r, c in data.gold_nodes:
            self.circle(self.x(c), self.y(r), size * W)
        self.pop()

    def on_exit_pair_silver(self):
        background.begin_draw()
        background.stroke(*SILVER)
        background.stroke_weight(2)
        background.no_fill()
        for r, c in data.silver_nodes:
            if (r, c) in data.silver_set:
                continue
            background.circle(self.x(c), self.y(r), 11)
        background.end_draw()
        data.silver_set.update(data.silver_nodes)
        data.silver_nodes = []

    def on_exit_silver_fast(self):
        self.on_exit_pair_silver()

    def on_exit_pair_gold(self):
        background.begin_draw()
        background.fill(*GOLD)
        background.no_stroke()
        for r, c in data.gold_nodes:
            if (r, c) in data.gold_set:
                continue
            background.circle(self.x(c), self.y(r), 5)
        background.end_draw()
        data.gold_set.update(data.gold_nodes)
        data.gold_nodes = []

    def on_exit_gold_fast(self):
        self.on_exit_pair_gold()

    def draw_totals(self):
        self.push()
        x0 = 350
        y0 = self.y(-0.5) + 30
        self.fill(*SILVER)
        self.text_align(self.RIGHT, self.BASELINE)
        self.text_size(30)
        self.text("Part 1: ", x0, y0)
        self.text_align(self.LEFT, self.BASELINE)
        self.text(f"{len(data.silver_set)}", x0, y0)
        self.fill(*GOLD)
        self.text_align(self.RIGHT, self.BASELINE)
        self.text_size(30)
        self.text("Part 2: ", x0, y0 + 60)
        self.text_align(self.LEFT, self.BASELINE)
        self.text(f"{len(data.gold_set)}", x0, y0 + 60)
        self.pop()

    def draw_frequencies(self, done=1.0):
        if data.current_state.id == "init":
            return
        self.push()
        n = len(data.frequencies)
        H = data.C * W / n
        y0 = self.y(-0.5)
        x0 = self.x(data.R + 0.5)
        self.color_mode(self.HSB, n, 100, 100)
        for i, frequency in enumerate(data.frequencies):
            if data.current_state.id == "show_frequencies" and i > 2 * data.done * n:
                break
            if frequency in data.done_frequencies:
                self.fill(i, 0, 80, 128)
                self.text(frequency, x0, y0 + H * i)
            elif frequency != data.frequency:
                self.fill(i, 80, 80)
                self.text(frequency, x0, y0 + H * i)
            else:
                self.fill(i, 80, 80)
                self.circle(x0, y0 + H * i, W)
                self.fill(i, 0, 80)
                self.text(frequency, x0, y0 + H * i)
        self.pop()

    def draw(self):
        data.tick()

        self.image(background, 0, 0)

        self.draw_totals()
        self.draw_frequencies()
        # self.text(data.current_state.id, 200, 100)
        if data.current_state == VisMachine.init:
            self.show_antennas(saturation=0.0)
        if data.current_state == VisMachine.show_frequencies:
            self.show_antennas(saturation=1 - 2 * abs(data.done - 0.5))
        elif data.current_state == VisMachine.start_frequency:
            self.draw_antennas(done=data.done, active_frequency=data.frequency)
        elif data.current_state == VisMachine.start_pair:
            self.draw_antennas(done=1.0, active_frequency=data.frequency)
            self.draw_pair_highlight(size=4 - 3 * data.done)
        elif data.current_state == VisMachine.show_line:
            self.draw_antennas(done=1.0, active_frequency=data.frequency)
            self.draw_pair_highlight(size=1.0)
            self.draw_line(data.antenna_a, data.antenna_b, done=data.done)
        elif data.current_state == VisMachine.pair_silver:
            self.draw_antennas(done=1.0, active_frequency=data.frequency)
            self.draw_pair_highlight(size=1.0)
            self.draw_line(data.antenna_a, data.antenna_b, done=1.0)
            self.draw_silver_antinodes(
                size=(3 - 2.5 * max(0.2, data.done)), alpha=data.done
            )
        elif data.current_state == VisMachine.pair_gold:
            self.draw_antennas(done=1.0, active_frequency=data.frequency)
            self.draw_pair_highlight(size=1.0)
            self.draw_line(data.antenna_a, data.antenna_b, done=1.0)
            self.draw_gold_antinodes(
                size=(3 - 2.5 * max(0.2, data.done)), alpha=data.done
            )
        elif data.current_state == VisMachine.end_pair:
            self.draw_antennas(done=1.0, active_frequency=data.frequency)
            self.draw_pair_highlight(size=1.0)
            self.draw_line(data.antenna_a, data.antenna_b, done=1.0)
        elif data.current_state == VisMachine.end_frequency:
            self.draw_antennas(done=1 - data.done, active_frequency=data.frequency)
        elif data.current_state == VisMachine.start_frequency_fast:
            self.draw_antennas(done=data.done, active_frequency=data.frequency)
        elif data.current_state == VisMachine.show_lines_fast:
            self.draw_antennas(done=1.0, active_frequency=data.frequency)
            for a1, a2 in data.antenna_pairs:
                self.draw_line(a1, a2, done=data.done)
        elif data.current_state == VisMachine.silver_fast:
            self.draw_antennas(done=1.0, active_frequency=data.frequency)
            for a1, a2 in data.antenna_pairs:
                self.draw_line(a1, a2, done=1.0)
            self.draw_silver_antinodes(
                size=(3 - 2.5 * max(0.2, data.done)), alpha=data.done
            )
        elif data.current_state == VisMachine.gold_fast:
            self.draw_antennas(done=1.0, active_frequency=data.frequency)
            for a1, a2 in data.antenna_pairs:
                self.draw_line(a1, a2, done=1.0)
            self.draw_gold_antinodes(
                size=(3 - 2.5 * max(0.2, data.done)), alpha=data.done
            )
