# Problem statement: https://adventofcode.com/2024/day/7

from py5 import Sketch  # , Py5Font
from aocd import get_data
from .day07 import day_title, reverse, is_possible, parse_input
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

FONT_SIZE = 30

WOP = 30  # operator column width

text = get_data(year=2024, day=7, block=True)


class VisMachine(StateMachine):
    # data fields
    ticks = 0
    duration = 0
    done = 1.0
    total_1 = 0
    total_2 = 0
    started = True
    data = parse_input(text)
    N = len(data)
    item_index = -1
    result = None
    numbers = []

    # animation stages

    init = State(initial=True)

    # start item
    start_item = State()
    next = init.to(start_item)

    def on_enter_start_item(self):
        self.duration = 6000
        self.item_index += 1
        self.result, self.numbers = self.data[self.item_index]

    # end item
    end_item = State()
    next |= start_item.to(end_item)

    def on_exit_end_item(self):
        self.total_1 += is_possible(self.result, self.numbers)
        self.total_2 += is_possible(self.result, self.numbers, operators="+*|")

    def has_next_item(self):
        return self.item_index + 1 < len(self.data)

    next |= end_item.to(start_item, cond="has_next_item")

    # finish animation
    end = State(final=True)

    next |= end_item.to(end, unless="has_next_item")

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

background = None


class VisSketch(Sketch):
    def settings(self):
        self.size(WIDTH, HEIGHT)
        self.smooth()

    def setup(self):
        self.window_title(f"Advent of Code 2024 - Day 7 - {day_title}")

        # prepare and measure font
        font = self.create_font("Liberation Mono", FONT_SIZE)
        self.text_font(font)

        self.rect_mode(self.CENTER)
        self.text_align(self.CENTER, self.CENTER)

        data.add_listener(self)

    def mouse_clicked(self):
        data.started = True

    def draw_number(self, n, x, y):
        self.push()
        self.stroke(*SILVER)
        self.no_fill()
        self.stroke_weight(FONT_SIZE + 10)
        w = self.text_width(str(n))
        self.line(x - w, y, x, y)
        self.fill(*BACKGROUND_2)
        self.no_stroke()
        self.text_align(self.RIGHT, self.CENTER)
        self.text(str(n), x, y)
        self.pop()
        return w

    def draw_item(self):
        if data.result is None:
            return
        self.push()
        n = len(data.numbers)
        W = (WIDTH - n * WOP) / (n + 1)
        self.fill(*TEXT_COLOR)
        self.stroke(*TEXT_COLOR)
        self.stroke_weight(1)
        self.line(0, 100, WIDTH, 100)
        for i in range(n):
            self.line((W + WOP) * i + W, 0, (W + WOP) * i + W, HEIGHT)
            self.line((W + WOP) * (i + 1), 0, (W + WOP) * (i + 1), HEIGHT)
            self.text(str(data.numbers[i]), (W + WOP) * i + W / 2, 50)
            self.text("?", (W + WOP) * (i + 1) - WOP / 2, 50)
        self.text(str(data.result), (W + WOP) * n + W / 2, 50)
        text = " ? ".join(map(str, data.numbers)) + " = " + str(data.result)
        self.text(text, WIDTH // 2, HEIGHT // 2)
        self.pop()

    def draw(self):
        data.tick()

        self.background(*BACKGROUND)
        self.draw_item()
        self.text(data.current_state.id, 300, 100)
        y0 = HEIGHT / 2
        w = self.draw_number(f" = {data.result}", WIDTH - 200, y0)
        self.stroke(*SILVER)
        self.no_fill()
        self.stroke_weight(FONT_SIZE + 10)
        self.line(WIDTH - 400, y0, WIDTH - 200 - w, y0)
        self.line(WIDTH - 400, y0 - 100, WIDTH - 200 - w, y0)
        self.line(WIDTH - 400, y0 + 100, WIDTH - 200 - w, y0)
        self.draw_number(" 1230+3", WIDTH - 400, y0 - 100)
        self.draw_number(" 411*3", WIDTH - 400, y0)
        self.draw_number(" 123||3", WIDTH - 400, y0 + 100)
        # self.draw_totals()
