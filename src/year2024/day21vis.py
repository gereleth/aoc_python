# Problem statement: https://adventofcode.com/2024/day/16

from py5 import Sketch  # , Py5Font
from aocd import data
from .day21 import day_title, numeric_keypad, directional_keypad, Keypad
from statemachine import StateMachine, State
from functools import cache

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


# copy pasted from solution - need to find actual sequences,
# not just their lengths
@cache
def best_controls_directional(code: str, level: int):
    """Find shortest sequence to enter `code` on a directional keypad
    through `level` layers of directional keypads"""
    seq = ""
    for basic_programs in directional_keypad.controls_for_code(code):
        if level == 0:
            seq += min((program for program in basic_programs), key=len)
        else:
            seq += min(
                (
                    best_controls_directional(program, level - 1)
                    for program in basic_programs
                ),
                key=len,
            )
    return seq


def best_controls_numeric(code: str, levels: int):
    """Find shortest sequence length to enter `code` on a numeric keypad
    through `levels` directional keypads"""
    seq = ""
    for basic_programs in numeric_keypad.controls_for_code(code):
        seq += min(
            (
                best_controls_directional(program, level=levels - 1)
                for program in basic_programs
            ),
            key=len,
        )
    return seq


class KeypadState:
    def __init__(self, keypad: Keypad):
        self.keypad = keypad
        self.r0, self.c0 = keypad.button_positions["A"]
        self.r, self.c = keypad.button_positions["A"]
        self.pushing = None

    def execute(self, command: str | None):
        self.r0, self.c0 = self.r, self.c
        self.pushing = None
        if command is None:
            return
        elif command == ">":
            self.r, self.c = self.r0, self.c0 + 1
        elif command == "<":
            self.r, self.c = self.r0, self.c0 - 1
        elif command == "^":
            self.r, self.c = self.r0 - 1, self.c0
        elif command == "v":
            self.r, self.c = self.r0 + 1, self.c0
        else:
            self.pushing = self.keypad.lines[self.r][self.c]
            return self.keypad.lines[self.r][self.c]
        return None

    def reset(self):
        self.r0, self.c0 = self.keypad.button_positions["A"]
        self.r, self.c = self.keypad.button_positions["A"]


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
    keypads = [
        KeypadState(directional_keypad),
        KeypadState(directional_keypad),
        KeypadState(directional_keypad),
        KeypadState(numeric_keypad),
    ]
    codes = text.split()
    code_index = -1
    code = ""
    entered_code = ""
    sequence = ""
    seq_index = -1
    code_done = False
    all_codes_done = False
    # animation stages

    init = State(initial=True)
    begin_code = State()
    enter_commands = State()
    finish_code = State()
    end = State(final=True)

    transition = (
        init.to(begin_code)
        | begin_code.to(enter_commands)
        | enter_commands.to.itself(unless="code_done")
        | enter_commands.to(finish_code)
        | finish_code.to(begin_code, unless="all_codes_done")
        | finish_code.to(end)
    )

    def on_enter_begin_code(self):
        self.duration = 1
        self.code_index += 1
        self.code = self.codes[self.code_index]
        self.entered_code = ""
        self.seq_index = -1
        self.sequence = best_controls_numeric(self.code, levels=2)
        for k in self.keypads:
            k.reset()
        self.all_codes_done = self.code_index == len(self.codes) - 1

    def on_enter_enter_commands(self):
        self.duration = 30
        self.seq_index += 1
        command = self.sequence[self.seq_index]
        self.keypads[0].pushing = command
        for keypad in self.keypads[1:]:
            command = keypad.execute(command)
        if command:
            self.entered_code += command
        self.code_done = self.entered_code == self.code

    def on_enter_finish_code(self):
        self.duration = 180

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
W = WIDTH // 4
imgs = []


class VisSketch(Sketch):
    def settings(self):
        self.size(WIDTH, HEIGHT)
        self.smooth()

    def setup(self):
        global background
        self.window_title(f"Advent of Code 2024 - Day 21 - {day_title}")

        # prepare and measure font
        font = self.create_font("Liberation Mono", FONT_SIZE)
        self.text_font(font)
        self.text_size(FONT_SIZE)

        self.rect_mode(self.CENTER)
        self.text_align(self.CENTER, self.CENTER)
        # background = self.create_graphics(WIDTH, HEIGHT)
        # background.begin_draw()
        # self.draw_walls(gr=background)
        # background.end_draw()
        imgs.extend(
            (
                self.load_image("christmas.jpg"),
                self.load_image("frost.jpg"),
                self.load_image("radioactive.jpg"),
                self.load_image("space.jpg"),
            )
        )
        data.add_listener(self)

    def mouse_clicked(self):
        if data.started:
            title = "-".join(day_title.lower().split())
            self.save_frame(f"2024-day21-{title}-{self.frame_count:03d}.png")
        data.started = not data.started

    def draw_keypad(self, x, y, keypadstate, cursor=True):
        self.push()
        self.fill(*BACKGROUND_2)
        self.rect(x, y, 300, 400)
        self.fill(*TEXT_COLOR, 128)
        self.rect(x, y, 300, 400)
        for r, line in enumerate(keypadstate.keypad.lines):
            for c, char in enumerate(line):
                if char == "X":
                    continue
                if char == keypadstate.pushing:
                    self.fill(*SILVER)
                else:
                    self.fill(*TEXT_COLOR)
                self.rect(x - 100 + 100 * c, y - 150 + 100 * r, 80, 80)
                self.fill(*BACKGROUND_2)
                self.text(char, x - 100 + 100 * c, y - 150 + 100 * r)
        if cursor:
            r = self.lerp(keypadstate.r0, keypadstate.r, data.done)
            c = self.lerp(keypadstate.c0, keypadstate.c, data.done)
            self.fill(0, 255, 0, 64)
            self.circle(x - 100 + 100 * c, y - 150 + 100 * r + 20, 20)
        self.pop()

    def draw_entered_code(self):
        self.push()
        self.fill(*TEXT_COLOR, 128)
        self.rect(7 * W / 2, 200, 300, 100)
        if data.current_state == VisMachine.finish_code:
            self.fill("#2ab34b")
        else:
            self.fill(*BACKGROUND_2)
        self.text_size(80)
        self.text_align(self.LEFT, self.CENTER)
        self.text(data.entered_code, 7 * W / 2 - 100, 200)
        if len(data.entered_code) < len(data.code):
            self.fill(90.0)
            n = len(data.entered_code)
            self.text(" " * n + data.code[n:], 7 * W / 2 - 100, 200)
        self.pop()

    def draw(self):
        data.tick()
        self.background(*BACKGROUND)
        for i, img in enumerate(imgs):
            self.image(img, i * W, 0)
        self.push()
        self.stroke_weight(10)
        self.stroke(*BACKGROUND_2)
        for i in range(1, 4):
            self.line(W * i, 0, W * i, HEIGHT)
        self.pop()
        self.draw_keypad(W / 2, 500, data.keypads[0], cursor=False)
        self.draw_keypad(3 * W / 2, 500, data.keypads[1])
        self.draw_keypad(5 * W / 2, 500, data.keypads[2])
        self.draw_keypad(7 * W / 2, 500, data.keypads[3])
        self.draw_entered_code()
