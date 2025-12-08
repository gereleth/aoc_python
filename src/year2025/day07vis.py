# Problem statement: https://adventofcode.com/2025/day/7

from math import log
from py5 import Sketch, Py5Font
from aocd import data
from collections import defaultdict
from statemachine import StateMachine, State
from .day07 import day_title, test_input
from matplotlib import colormaps

# print(Py5Font.list()) # list available fonts

WIDTH = 1920
HEIGHT = 1080

SILVER = (153, 153, 204)
GOLD = (230, 230, 94)
TEXT_COLOR = (204, 204, 204)
BACKGROUND = (15, 15, 35)
BACKGROUND_2 = (25, 25, 55)
WHITE = (255, 255, 255)

FONT_SIZE = 30
LEADING = FONT_SIZE
colormap = colormaps.get("plasma")


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

    def on_enter_init(self):
        self.lines = test_input.split("\n")  # data.split("\n")
        self.R = len(self.lines)
        self.C = len(self.lines[0])
        self.c0 = self.lines[0].index("S")
        self.splitters = [
            (r, c)
            for r in range(self.R)
            for c in range(self.C)
            if self.lines[r][c] == "^"
        ]
        self.beams = {0: {(self.c0, self.c0): 1}}

    beams_travel = State()
    next = init.to(beams_travel)

    def on_enter_beams_travel(self):
        self.duration = max(2, min(30, 30 - len(self.beams) // 2))

    beams_split = State()
    next |= beams_travel.to(beams_split, unless="is_finished")

    def on_enter_beams_split(self):
        self.duration = 0
        r = len(self.beams)
        new_beams = defaultdict(int)
        for (_, c), count in self.beams[r - 1].items():
            if self.lines[r][c] == "^":
                new_beams[(c, c - 1)] += count
                new_beams[(c, c + 1)] += count
            elif self.lines[r][c] == ".":
                new_beams[(c, c)] += count
        self.beams[r] = new_beams
        if len(self.beams) == self.R:
            self.is_finished = True

    next |= beams_split.to(beams_travel)

    # finish animation
    end = State(final=True)
    next |= beams_travel.to(end, cond="is_finished")

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


vis = VisMachine()

W = min((WIDTH) // (vis.C + 1), (HEIGHT) // (vis.R + 1))
PW = (WIDTH - vis.C * W) // 2
PH = (HEIGHT - vis.R * W) // 2
background = None


class VisSketch(Sketch):
    def settings(self):
        self.size(WIDTH, HEIGHT)
        self.smooth()

    def setup(self):
        self.window_title(f"Advent of Code 2025 - Day 7 - {day_title}")

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
        background.text_font(font)
        background.text_leading(LEADING)
        self.draw_splitters(graphics=background)
        self.draw_start(graphics=background)
        background.end_draw()

        vis.add_listener(self)

    def mouse_clicked(self):
        if vis.started:
            title = "-".join(s.lower() for s in day_title.split())
            self.save_frame(f"outputs/2025-day07-{title}-{self.frame_count}.png")
        vis.started = not vis.started

    def x(self, c):
        return PW + c * W

    def y(self, r):
        return PH + r * W

    def on_exit_beams_travel(self):
        background.begin_draw()
        self.draw_beams(done=1, graphics=background)
        background.end_draw()

    def draw_start(self, graphics=None):
        g = graphics if graphics else self
        g.push()
        g.fill(*GOLD)
        g.no_stroke()
        g.circle(self.x(vis.c0), self.y(0), W * 0.8)
        g.pop()

    def draw_splitter(self, r, c, graphics=None):
        g = graphics if graphics else self
        g.push()
        g.fill(*SILVER)
        g.no_stroke()
        g.quad(
            self.x(c) - W,
            self.y(r) + W,
            self.x(c),
            self.y(r),
            self.x(c) + W,
            self.y(r) + W,
            self.x(c),
            self.y(r) + W * 0.75,
        )
        g.pop()

    def draw_splitters(self, graphics=None):
        g = graphics if graphics else self
        g.push()
        for r, c in vis.splitters:
            self.draw_splitter(r, c, graphics=graphics)
        g.pop()

    def draw_beams(self, done, graphics=None):
        g = graphics if graphics else self
        g.push()
        g.stroke(*GOLD)
        g.stroke_weight(max(3, W / 8))
        r = len(vis.beams) - 1
        max_count = max(vis.beams[r].values())
        g.text_align(self.LEFT, self.CENTER)
        for (c1, c2), count in vis.beams[r].items():
            rd, gr, bl, _ = colormap(
                self.constrain(log(count + 1) / log(max_count + 1), 0.2, 1.0)
            )
            g.stroke(int(255 * rd), int(255 * gr), int(255 * bl))
            # g.stroke(*GOLD, 255 * log(count + 1) / log(max_count + 1))
            g.line(
                self.x(c1),
                self.y(r),
                self.x(c1) + done * (self.x(c2) - self.x(c1)),
                self.y(r) + W * done,
            )
            if r % 2 == 1 and W > FONT_SIZE:
                g.text(str(count), self.x(c1 + 0.1), self.y(r + 0.5))
        g.pop()

    def draw(self):
        vis.tick()
        self.image(background, 0, 0)
        # print(vis.beams)
        if vis.current_state == vis.beams_travel:
            self.draw_beams(vis.done)
