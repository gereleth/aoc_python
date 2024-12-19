# Problem statement: https://adventofcode.com/2024/day/19

from py5 import Sketch  # , Py5Font
from aocd import data
from .day19 import day_title, parse_input
from statemachine import StateMachine, State
from collections import Counter

# print(Py5Font.list()) # list available fonts

WIDTH = 1920
HEIGHT = 1080
PADDING = 200

SILVER = (153, 153, 204)
GOLD = (230, 230, 94)
TEXT_COLOR = (204, 204, 204)
BACKGROUND = (15, 15, 35)
BACKGROUND_2 = (25, 25, 55)
WHITE = (255, 255, 255)

FONT_SIZE = 20

text = data  # aocd magic, gets correct input by inspecting filepath for year/day
towels, designs = parse_input(data)
C = max(len(d) for d in designs)
W = (WIDTH - PADDING) // C
PW = min(50, (WIDTH - C * W) // 2)
COLORS = {
    "r": "#eb1a3a",
    "g": "#2ab34b",
    "b": "#0c131f",
    "u": "#0773bb",
    "w": "#eaeaea",
}


class VisMachine(StateMachine):
    # data fields
    started = True
    ticks = 0
    duration = 0
    done = 1.0
    total_1 = 0
    total_2 = 0
    is_finished = False
    # task data
    design_index = 0
    design = designs[0]
    ways = Counter()
    ways[""] = 1
    index = 0
    splits = []
    design_done = False
    all_designs_done = False
    # animation stages

    init = State(initial=True)
    check_tail = State()

    def on_enter_check_tail(self):
        self.duration = max(1, 60 - 3 * self.index)
        self.index += 1
        tail = self.design[-self.index :]
        self.splits = list(towels.get_splits(tail))
        self.ways[tail] = sum(self.ways[r] for t, r in self.splits)
        self.design_done = self.design == tail

    finish_design = State()

    def on_enter_finish_design(self):
        self.duration = 120
        self.all_designs_done = self.design_index == len(designs) - 1

    next_design = State()

    def on_enter_next_design(self):
        self.duration = 0
        self.design_index += 1
        self.design = designs[self.design_index]
        self.index = 0
        self.splits = []
        self.design_done = False

    end = State(final=True)

    transition = (
        init.to(check_tail)
        | check_tail.to.itself(unless="design_done")
        | check_tail.to(finish_design, cond="design_done")
        | finish_design.to(next_design, unless="all_designs_done")
        | next_design.to(check_tail)
        | finish_design.to(end, cond="all_designs_done")
    )

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
background = None


class VisSketch(Sketch):
    def settings(self):
        self.size(WIDTH, HEIGHT)
        self.smooth()

    def setup(self):
        global background
        self.window_title(f"Advent of Code 2024 - Day 19 - {day_title}")

        # prepare and measure font
        font = self.create_font("Liberation Mono", FONT_SIZE)
        self.text_font(font)

        self.rect_mode(self.CENTER)
        self.text_align(self.LEFT, self.CENTER)
        self.background(*BACKGROUND)

        data.add_listener(self)

    def mouse_clicked(self):
        data.started = not data.started
        # pass
        # self.save_frame(f"image{self.frame_count:03d}.png")

    def draw_design(self):
        self.push()
        self.stroke(180, 180, 180)
        self.stroke_weight(3)
        for i, char in enumerate(data.design):
            self.fill((COLORS[char]))
            self.rect(PW + i * W, HEIGHT // 3, W - 2, 2 * W - 2)
        self.pop()
        self.push()
        for i in range(data.index):
            tail = data.design[-i - 1 :]
            relevant = any(tail == split[1] for split in data.splits)
            self.fill(*TEXT_COLOR, 255 if relevant else 128)
            self.push_matrix()
            self.translate(PW + (len(data.design) - 1 - i) * W, HEIGHT // 3 - 1.5 * W)
            self.rotate(-self.PI / 4)
            if i == data.index - 1:
                self.fill(*SILVER)
            if tail == data.design:
                self.fill(*GOLD)
            self.text(str(data.ways[data.design[-i - 1 :]]), 0, 0)
            self.pop_matrix()
        self.pop()

    def draw_splits(self):
        self.push()
        x0 = PW + (len(data.design) - data.index) * W
        y0 = HEIGHT // 3 + 3 * W
        self.stroke(180, 180, 180)
        self.stroke_weight(3)
        for towel, rest in data.splits:
            if len(rest) > 0:
                # plus sign
                self.line(x0 + (len(towel) - 1) * W, y0, x0 + (len(towel) + 0) * W, y0)
                self.line(
                    x0 + (len(towel) - 0.25) * W,
                    y0 - W / 4,
                    x0 + (len(towel) - 0.25) * W,
                    y0 + W / 4,
                )
            for i, char in enumerate(towel):
                self.fill((COLORS[char]))
                self.rect(x0 + i * W, y0, W - 2, 2 * W - 2)
            for i, char in enumerate(rest):
                self.fill((COLORS[char]))
                self.rect(x0 + (len(towel) + 0.5 + i) * W, y0, W - 2, 2 * W - 2)
            self.fill(*TEXT_COLOR)
            self.text(str(data.ways[rest]), x0 + (len(towel) + len(rest) + 1) * W, y0)
            y0 += 3 * W
        self.pop()

    def draw(self):
        data.tick()

        self.background(*BACKGROUND)
        self.draw_design()
        self.draw_splits()
        # self.fill(*GOLD)
        # self.text(f"state={data.current_state.id}", 100, 130)
