# Problem statement: https://adventofcode.com/2024/day/20

from py5 import Sketch  # , Py5Font
from aocd import data
from .day20 import day_title, RaceConditionMaze
from statemachine import StateMachine, State
from matplotlib import colormaps
import numpy as np
from itertools import islice, cycle
from collections import Counter

# print(Py5Font.list()) # list available fonts
colormap_bright = colormaps.get("plasma")

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
FONT_SIZE = 30

text = data  # aocd magic, gets correct input by inspecting filepath for year/day


class VisMaze(RaceConditionMaze):
    def cheat_gains_point(self, point, cheat_steps=2, min_gain=1):
        dist_start = self.distance_from_start[point]
        r0, c0 = point
        rmin = max(0, r0 - cheat_steps)
        rmax = min(self.R, r0 + cheat_steps + 1)
        for r in range(rmin, rmax):
            dr = abs(r - r0)
            csteps = cheat_steps - dr
            cmin = max(0, c0 - csteps)
            cmax = min(self.C, c0 + 1 + csteps)
            for c in range(cmin, cmax):
                pos = (r, c)
                d = self.distance_from_start.get(pos, -1)
                if d < dist_start:
                    continue
                gain = d - dist_start - dr - abs(c0 - c)
                if gain >= min_gain:
                    yield gain, (r0, c0), pos


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
    maze = VisMaze(text)
    path = sorted(maze.distance_from_start, key=maze.distance_from_start.get)
    path_index = 0
    color_max_cost = 1.2 * maze.no_cheat_cost
    path_done = False
    tiles_buffer = []
    silver_gains_buffer = []
    gold_gains_buffer = []
    # animation stages

    init = State(initial=True)

    show_path = State()

    transition = init.to(show_path)

    def on_enter_show_path(self):
        self.duration = 1
        duration = 180
        items_per_frame = max(1, len(self.path) // duration)
        portion = self.path[self.path_index : self.path_index + items_per_frame]
        self.tiles_buffer.extend(portion)
        self.path_index += items_per_frame
        self.path_done = self.path_index >= len(self.path) - 1

    transition |= show_path.to.itself(unless="path_done")

    begin_silver_scan = State()
    transition |= show_path.to(begin_silver_scan, cond="path_done")

    def on_enter_begin_silver_scan(self):
        self.duration = 60
        self.path_index = 0
        self.path_done = False

    silver_scan = State()

    def on_enter_silver_scan(self):
        self.duration = 1
        self.items_per_frame = 1 if self.path_index < 200 else 100
        for _ in range(self.items_per_frame):
            point = self.path[self.path_index]
            self.silver_gains_buffer.extend(
                self.maze.cheat_gains_point(point, cheat_steps=2, min_gain=100)
            )
            self.path_index += 1
            self.path_done = self.path_index == len(self.path)
            if self.path_done:
                self.path_index = 0
                break

    transition |= begin_silver_scan.to(silver_scan)
    transition |= silver_scan.to.itself(unless="path_done")

    begin_gold_scan = State()
    transition |= silver_scan.to(begin_gold_scan, cond="path_done")

    def on_enter_begin_gold_scan(self):
        self.duration = 60
        self.path_index = 0
        self.path_done = False

    gold_scan = State()
    transition |= begin_gold_scan.to(gold_scan)
    transition |= gold_scan.to.itself(unless="path_done")

    def on_enter_gold_scan(self):
        self.duration = 1
        self.items_per_frame = 1 if self.path_index < 200 else 10
        data.gold_gains_buffer.clear()
        for _ in range(self.items_per_frame):
            point = self.path[self.path_index]
            self.gold_gains_buffer.extend(
                self.maze.cheat_gains_point(point, cheat_steps=20, min_gain=100)
            )
            self.path_index += 1
            self.path_done = self.path_index == len(self.path)
            if self.path_done:
                self.path_index = 0
                break

    # finish animation
    end = State(final=True)
    transition |= gold_scan.to(end, cond="path_done")

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


# from itertools recipes
def roundrobin(*iterables):
    "Visit input iterables in a cycle until each is exhausted."
    # roundrobin('ABC', 'D', 'EF') → A D E B F C
    # Algorithm credited to George Sakkis
    iterators = map(iter, iterables)
    for num_active in range(len(iterables), 0, -1):
        iterators = cycle(islice(iterators, num_active))
        yield from map(next, iterators)


def make_cheat_contour(cheat_time: int):
    n = cheat_time + 1
    contour = [
        *roundrobin(
            ((i + 0.5, -(i + 0.5 - n)) for i in range(n)),
            ((i + 0.5, -(i + 1.5 - n)) for i in range(n - 1)),
        ),
        *roundrobin(
            ((n - i - 0.5, -i - 0.5) for i in range(n)),
            ((n - i - 1.5, -i - 0.5) for i in range(n - 1)),
        ),
        *roundrobin(
            ((-i - 0.5, -n + i + 0.5) for i in range(n)),
            ((-i - 0.5, -n + i + 1.5) for i in range(n - 1)),
        ),
        *roundrobin(
            ((-n + 0.5 + i, i + 0.5) for i in range(n)),
            ((-n + 1.5 + i, i + 0.5) for i in range(n - 1)),
        ),
    ]
    contour.append(contour[0])  # close the shape
    return np.array(contour) * W


silver_contour = make_cheat_contour(2)
gold_contour = make_cheat_contour(20)


class VisSketch(Sketch):
    def settings(self):
        self.size(WIDTH, HEIGHT)
        self.smooth()

    def setup(self):
        global background
        self.window_title(f"Advent of Code 2024 - Day 20 - {day_title}")

        # prepare and measure font
        font = self.create_font("Liberation Mono", FONT_SIZE)
        self.text_font(font)
        self.text_size(FONT_SIZE)

        self.rect_mode(self.CENTER)
        self.text_align(self.CENTER, self.CENTER)
        background = self.create_graphics(WIDTH, HEIGHT)
        background.begin_draw()
        self.draw_walls(gr=background)
        background.end_draw()

        data.add_listener(self)

    def mouse_clicked(self):
        data.started = not data.started
        pass
        # self.save_frame(f"image{self.frame_count:03d}.png")

    def draw_walls(self, gr=None):
        g = self if gr is None else gr
        g.push()
        g.rect_mode(self.CORNER)
        g.background(*BACKGROUND)
        g.fill(*BACKGROUND_2)
        g.stroke(*WALL_COLOR)
        g.rect(PW - W / 2, PH - W / 2, C * W, R * W)
        g.fill(*WALL_COLOR, 32)
        g.rect(PW - W / 2, PH - W / 2, C * W, R * W)
        g.rect_mode(self.CENTER)
        g.fill(*WALL_COLOR, 64)
        g.no_stroke()
        for r, line in enumerate(data.maze.lines):
            for c, char in enumerate(line):
                if char == "#":
                    g.rect(PW + c * W, PH + r * W, W, W)
        g.pop()

    def draw_tiles(self, gr=None):
        g = self if gr is None else gr
        g.push()
        g.rect_mode(self.CENTER)
        g.no_stroke()
        for r, c in data.tiles_buffer:
            d = data.maze.distance_from_start[(r, c)]
            color = colormap_bright(0.2 + 0.8 * d / data.color_max_cost)
            g.fill(*(int(255 * c) for c in color))
            g.rect(PW + c * W, PH + r * W, W, W)
        g.pop()
        data.tiles_buffer.clear()

    def draw_scan_contour(self):
        self.push()
        self.stroke_weight(3)
        self.shape_mode(self.LINES)
        self.no_fill()
        if data.current_state == VisMachine.silver_scan:
            self.stroke(*SILVER)
            contour = silver_contour
            r, c = data.path[data.path_index]
            x = PW + W * c
            y = PH + W * r
            self.begin_shape()
            self.vertices(contour + np.array([x, y]))
            self.end_shape()
            self.fill(*SILVER)
            self.no_stroke()
            self.circle(x, y, W / 2)
        elif data.current_state == VisMachine.gold_scan:
            self.stroke(*GOLD)
            contour = gold_contour
            r, c = data.path[data.path_index]
            x = PW + W * c
            y = PH + W * r
            self.begin_shape()
            self.vertices(contour + np.array([x, y]))
            self.end_shape()
            self.fill(*GOLD)
            self.no_stroke()
            self.circle(x, y, W / 2)
        self.pop()

    def draw_cheat_gains_silver(self, gr=None):
        g = self if gr is None else gr
        g.push()
        g.no_fill()
        g.stroke(*SILVER)
        # g.stroke_weight(4)
        for gain, (r1, c1), (r2, c2) in data.silver_gains_buffer:
            g.stroke(*SILVER)
            g.stroke_weight(5)
            g.line(PW + W * c1, PH + W * r1, PW + W * c2, PH + W * r2)
            color = colormap_bright(gain * 4 / data.color_max_cost)
            g.stroke(*(int(255 * i) for i in color))
            g.stroke_weight(3)
            g.line(PW + W * c1, PH + W * r1, PW + W * c2, PH + W * r2)
        g.pop()
        data.silver_gains_buffer.clear()

    def draw_cheat_gains_gold(self, gr=None):
        g = self if gr is None else gr
        g.push()
        g.no_fill()
        g.stroke(*GOLD)
        g.stroke_weight(1)
        p1 = data.gold_gains_buffer[-1][1]
        for gain, (r1, c1), (r2, c2) in data.gold_gains_buffer:
            if (r1, c1) != p1:
                continue
            # color = colormap_bright(gain * 2 / data.color_max_cost)
            # g.stroke(*(int(255 * i) for i in color))
            g.line(PW + W * c1, PH + W * r1, PW + W * c2, PH + W * r2)
        g.pop()
        # data.gold_gains_buffer.clear()

    def draw_cheat_gains_gold_bg(self, gr=None):
        g = self if gr is None else gr
        g.push()
        g.fill(*GOLD)
        starts = Counter()
        for gain, p1, p2 in data.gold_gains_buffer:
            starts[p1] += gain
        for (r, c), sum_gain in starts.items():
            color = colormap_bright(sum_gain / (20 * data.color_max_cost))
            g.fill(*(int(255 * i) for i in color))
            g.circle(PW + W * c, PH + W * r, 0.3 * np.log10(sum_gain) * W)
        g.pop()

    def draw(self):
        data.tick()
        self.image(background, 0, 0)
        # self.draw_totals()
        if data.tiles_buffer:
            background.begin_draw()
            self.draw_tiles(gr=background)
            background.end_draw()
        if data.silver_gains_buffer:
            background.begin_draw()
            self.draw_cheat_gains_silver(gr=background)
            background.end_draw()
        if data.gold_gains_buffer:
            background.begin_draw()
            self.draw_cheat_gains_gold(gr=self)
            self.draw_cheat_gains_gold_bg(gr=background)
            background.end_draw()
        self.draw_scan_contour()
