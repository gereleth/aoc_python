# Problem statement: https://adventofcode.com/2024/day/15

from py5 import Sketch  # , Py5Font
from aocd import data
from .day15 import day_title, Warehouse, BigWarehouse
from statemachine import StateMachine, State
from matplotlib import colormaps

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
WALL_COLOR = (200, 200, 200)
FONT_SIZE = 30


# aocd magic, gets correct input by inspecting filepath for year/day
wh_text, instructions = data.split("\n\n")
instructions = "".join(instructions.split())


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
    wh = Warehouse(wh_text)
    index_1 = -1
    index_2 = -1
    time_per_tick = 1
    finished_1 = False
    finished_2 = False
    in_big_wh = False
    bigwh = BigWarehouse(wh_text)
    # animation stages

    init = State(initial=True)

    step = State()
    next = init.to(step)

    def on_enter_step(self):
        self.duration = max(1, 5 - data.index_1 // 20)
        if self.duration == 1:
            self.time_per_tick = min(self.time_per_tick + 1, 20)
        for _ in range(min(self.time_per_tick, len(instructions) - 1 - self.index_1)):
            self.index_1 += 1
            self.wh.maybe_move(instructions[self.index_1])
        self.finished_1 = self.index_1 + 1 == len(instructions)

    next |= step.to.itself(unless="finished_1")

    count_score_1 = State()
    next |= step.to(count_score_1)

    def on_enter_count_score_1(self):
        self.duration = 120

    show_score_1 = State()
    next |= count_score_1.to(show_score_1)

    def on_enter_show_score_1(self):
        self.duration = 120
        self.total_1 = self.wh.calc_gps()

    def on_exit_show_score_1(self):
        self.in_big_wh = True
        self.time_per_tick = 1

    step2 = State()
    next |= show_score_1.to(step2)

    def on_enter_step2(self):
        self.duration = max(1, 5 - data.index_2 // 20)
        if self.duration == 1:
            self.time_per_tick = min(self.time_per_tick + 1, 20)
        for _ in range(min(self.time_per_tick, len(instructions) - 1 - self.index_2)):
            self.index_2 += 1
            self.bigwh.maybe_move(instructions[self.index_2])
        self.finished_2 = self.index_2 + 1 == len(instructions)

    next |= step2.to.itself(unless="finished_2")

    count_score_2 = State()
    next |= step2.to(count_score_2)

    def on_enter_count_score_2(self):
        self.duration = 120

    show_score_2 = State()
    next |= count_score_2.to(show_score_2)

    def on_enter_show_score_2(self):
        self.duration = 120
        self.total_2 = self.bigwh.calc_gps()

    def on_exit_show_score_2(self):
        self.time_per_tick = 1

    # finish animation
    end = State(final=True)
    next |= show_score_2.to(end)

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
R = data.wh.R
C1 = data.wh.C
C2 = data.bigwh.C
W = min((HEIGHT - 20) // R, (WIDTH - 20) // C2)
PW1 = (WIDTH - C1 * W) // 2
PH = (HEIGHT - R * W) // 2
PW2 = (WIDTH - C2 * W) // 2
background = None
instruction_widths = []


class VisSketch(Sketch):
    def settings(self):
        self.size(WIDTH, HEIGHT)
        self.smooth()

    def setup(self):
        global background
        self.window_title(f"Advent of Code 2024 - Day 15 - {day_title}")

        # prepare and measure font
        font = self.create_font("Liberation Mono", FONT_SIZE)
        self.text_font(font)
        for f in range(FONT_SIZE, 0, -2):
            self.text_size(f)
            instruction_widths.append(self.text_width(">"))
        self.text_size(FONT_SIZE)

        self.rect_mode(self.CENTER)
        self.text_align(self.CENTER, self.CENTER)
        background = self.create_graphics(WIDTH, HEIGHT)
        background.begin_draw()
        self.draw_walls(gr=background)
        background.end_draw()

        data.add_listener(self)

    def on_exit_show_score_1(self):
        background.begin_draw()
        self.draw_walls(gr=background, stage=2)
        background.end_draw()

    def mouse_clicked(self):
        data.started = not data.started
        pass
        # self.save_frame(f"image{self.frame_count:03d}.png")

    def draw_walls(self, gr=None, stage=1):
        g = self if gr is None else gr
        g.push()
        g.rect_mode(self.CORNER)
        g.background(*BACKGROUND)
        g.fill(*BACKGROUND_2)
        g.stroke(*WALL_COLOR)
        if stage == 1:
            g.rect(
                PW1 - W / 2,
                PH - W / 2,
                C1 * W,
                R * W,
            )
        else:
            g.rect(
                PW2 - W / 2,
                PH - W / 2,
                C2 * W,
                R * W,
            )
        g.rect_mode(self.CENTER)
        g.fill(*WALL_COLOR)
        g.no_stroke()
        if stage == 1:
            for r, line in enumerate(data.wh.lines):
                for c, char in enumerate(line):
                    if char == "#":
                        g.rect(PW1 + c * W, PH + r * W, W, W)
        else:
            for r, line in enumerate(data.bigwh.lines):
                for c, char in enumerate(line):
                    if char == "#":
                        g.rect(PW2 + c * W, PH + r * W, W, W)
        g.pop()

    def draw_boxes(self):
        self.push()
        self.rect_mode(self.CENTER)
        self.stroke_weight(2)
        if not data.in_big_wh:
            self.stroke(*SILVER)
            alpha = 128
            for r, line in enumerate(data.wh.lines):
                if data.current_state == VisMachine.count_score_1:
                    alpha = 128 + int(128 * max(0, 1.0 - abs(r - data.done * R)))
                self.fill(*SILVER, alpha)
                for c, char in enumerate(line):
                    if char == "O":
                        self.rect(PW1 + c * W, PH + r * W, W - 4, W - 4)
        else:
            self.stroke(*GOLD)
            alpha = 128
            for r, line in enumerate(data.bigwh.lines):
                if data.current_state == VisMachine.count_score_2:
                    alpha = 128 + int(128 * max(0, 1.0 - abs(r - data.done * R)))
                self.fill(*GOLD, alpha)
                for c, char in enumerate(line):
                    if char == "[":
                        self.rect(PW2 + c * W + W / 2, PH + r * W, W * 2 - 4, W - 4)
        self.pop()

    def draw_robot(self):
        if not data.finished_1:
            index = max(data.index_1, 0)
            x = PW1 + data.wh.c0 * W
            y = PH + data.wh.r0 * W
        else:
            index = max(data.index_2, 0)
            x = PW2 + data.bigwh.c0 * W
            y = PH + data.bigwh.r0 * W
        self.push()
        self.fill(255, 0, 0, 196)
        self.no_stroke()
        self.circle(x, y, W)
        self.fill(*WHITE)
        self.text_size(20)
        self.text(instructions[index], x, y)
        self.pop()

    def draw_instructions(self):
        if not data.in_big_wh:
            index = max(data.index_1, 0)
            PW = PW2
            C = C2
            color = SILVER
        else:
            index = max(data.index_2, 0)
            PW = PW2
            C = C2
            color = GOLD
        size = FONT_SIZE
        n = size // 2 - 2
        done = index / (len(instructions) - 1)
        w_current = instruction_widths[0]
        w_before = sum(instruction_widths[1 : 1 + index])
        w_after = sum(instruction_widths[1 : len(instructions) - index])
        x0 = max(w_before, done * W * C) + w_current / 2
        x0 = min(W * C - W / 2 - w_after - w_current / 2, x0)
        self.push()
        y0 = PH + W * R + W
        # current and after
        xa = PW + x0
        xb = PW + x0
        self.rect_mode(self.CENTER)
        self.stroke(*color)
        self.no_fill()
        self.rect(xa, y0, instruction_widths[0], FONT_SIZE)
        self.fill(*color)
        self.no_stroke()
        self.text_size(size)
        self.text(instructions[index], xa, y0)
        xa += instruction_widths[0] / 2 + instruction_widths[1] / 2
        xb -= instruction_widths[0] / 2 + instruction_widths[1] / 2
        for i in range(1, n + 1):
            self.text_size(FONT_SIZE - 2 * i)
            if index + i < len(instructions):
                self.text(instructions[index + i], xa, y0)
                xa += instruction_widths[i] / 2 + instruction_widths[i + 1] / 2
            if index - i >= 0:
                self.text(instructions[index - i], xb, y0)
                xb -= instruction_widths[i] / 2 + instruction_widths[i + 1] / 2
        self.stroke(*color)
        if xb > PW:
            self.line(PW, y0, xb, y0)
        if xa < PW + W * C - W / 2:
            self.line(xa, y0, PW + W * C - W / 2, y0)
        self.pop()

    def draw_totals(self):
        self.push()
        y0 = PH - 2 * W
        x1 = PW1 - W / 2
        self.text_size(FONT_SIZE)
        self.fill(*SILVER)
        self.text_align(self.LEFT, self.CENTER)
        self.text(f"Part 1: {data.total_1}", x1, y0)

        self.fill(*GOLD)
        self.text_align(self.RIGHT, self.CENTER)
        x2 = PW1 + W * C1 - W / 2
        self.text(f"Part 2: {data.total_2}", x2, y0)
        self.pop()

    def draw(self):
        data.tick()
        self.image(background, 0, 0)
        self.draw_boxes()
        self.draw_robot()
        self.draw_instructions()
        self.draw_totals()
