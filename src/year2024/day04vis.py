# Problem statement: https://adventofcode.com/2024/day/4

from collections import defaultdict
import random
from py5 import Sketch, Py5Font
from aocd import get_data
import numpy as np
from .day04 import day_title

# print(Py5Font.list()) # list available fonts

WIDTH = 1920
HEIGHT = 1080
PADDING = 36
SILVER = (153, 153, 204)
SILVER_DARK = (64, 64, 99)
GOLD = (230, 230, 94)
GOLD_DARK = (83, 83, 60)
TEXT_COLOR = (204, 204, 204)
BACKGROUND = (15, 15, 35)
BACKGROUND_2 = (25, 25, 55)
FADED_COLOR = (75, 75, 90)
TEXT_COLOR = (204, 204, 204)
WHITE = (255, 255, 255)

text = get_data(year=2024, day=4, block=True)
lines = text.split("\n")

started = False
start_frame = 0

FONT_SIZE = 22
LEADING = FONT_SIZE * 1.0  # line height
W = -1  # single letter width, actual value calculated in setup
background = None
lines = lines[: int(HEIGHT // LEADING) + 1]


def part1():
    R, C = len(lines), len(lines[0])
    steps = [(0, 1), (1, 0), (1, 1), (1, -1)]
    items = defaultdict(list)
    for r in range(R):
        for c in range(C):
            for dr, dc in steps:
                if (
                    r + 3 * dr < 0
                    or r + 3 * dr >= R
                    or c + 3 * dc < 0
                    or c + 3 * dc >= C
                ):
                    continue
                word = "".join(lines[r + i * dr][c + i * dc] for i in range(4))
                if word == "XMAS":
                    items[(dr, dc)].append((r, c))
                elif word == "SAMX":
                    items[(-dr, -dc)].append((r + 3 * dr, c + 3 * dc))
    return items


def part2():
    R, C = len(lines), len(lines[0])
    items = []
    wanted = ("MAS", "SAM")
    diagonal_1 = ((-1, -1), (0, 0), (1, 1))
    diagonal_2 = ((1, -1), (0, 0), (-1, 1))
    for r in range(1, R - 1):
        for c in range(1, C - 1):
            if lines[r][c] != "A":
                continue
            word_1 = "".join(lines[r + dr][c + dc] for dr, dc in diagonal_1)
            word_2 = "".join(lines[r + dr][c + dc] for dr, dc in diagonal_2)
            if word_1 in wanted and word_2 in wanted:
                items.append((r, c))
    random.shuffle(items)
    return items


silver_items = part1()
gold_items = part2()

# arrays for silver highlight lines
silver_lines = {}
for offset, points in silver_items.items():
    silver_lines[offset] = np.zeros((len(points), 4))

# array for gold lines
gold_lines_start = np.zeros((len(gold_items), 2))

# (dr, dc) - listed clockwise, starting from how we normally read
offsets = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]


class VisSketch(Sketch):
    def settings(self):
        self.size(WIDTH, HEIGHT)
        self.smooth()

    def setup(self):
        global W, background, silver_lines, PADDING
        self.window_title(f"Advent of Code 2024 - Day 4 - {day_title}")

        # prepare and measure font
        font = self.create_font("Liberation Mono", FONT_SIZE)
        self.text_font(font)
        self.text_leading(LEADING)
        W = self.text_width("w")
        PADDING = max(0, (WIDTH - W * len(lines[0])) / 2)

        # prepare background with raw text
        background = self.create_graphics(WIDTH, HEIGHT)
        background.begin_draw()
        background.background(*BACKGROUND)
        background.text_font(font)
        background.text_leading(LEADING)
        background.fill(*TEXT_COLOR, 64)
        background.text(text, PADDING, PADDING, WIDTH - 2 * PADDING)
        background.end_draw()

        # prepare silver line positions
        for offset, points in silver_items.items():
            silver_lines[offset][:, 0] = [PADDING + c * W + W / 2 for (_, c) in points]
            silver_lines[offset][:, 1] = [
                PADDING + r * LEADING - LEADING / 2 + 3 for (r, _) in points
            ]

        # prepare gold line positions
        gold_lines_start[:, 0] = [PADDING + c * W + W / 2 for (_, c) in gold_items]
        gold_lines_start[:, 1] = [
            PADDING + r * LEADING - LEADING / 2 + 3 for (r, _) in gold_items
        ]

    def mouse_clicked(self):
        global started, start_frame
        started = True
        start_frame = self.frame_count

    def calc_stage(self):
        if started:
            f = self.frame_count - start_frame
        else:
            return "init", None
        FRAMES_PER_LETTER = 30
        FRAMES_PER_OFFSET = FRAMES_PER_LETTER * 5
        TOTAL_SILVER_FRAMES = FRAMES_PER_OFFSET * 8
        # TOTAL_SILVER_FRAMES = 0
        if f < TOTAL_SILVER_FRAMES:
            stage = "silver"
            offsets_done = f / FRAMES_PER_OFFSET
            letters_done = (f % FRAMES_PER_OFFSET) / FRAMES_PER_LETTER
            return stage, (offsets_done, letters_done)
        else:
            f -= TOTAL_SILVER_FRAMES
            NEW_ITEM_EVERY = 1
            ITEM_DURATION = 120
            stage = "gold"
            done = (f - ITEM_DURATION) / NEW_ITEM_EVERY
            if done > 0 and done == int(done) and done <= len(gold_items):
                done_index = int(done) - 1
            else:
                done_index = None
            animating = []
            for delta in range(0, ITEM_DURATION + 1, NEW_ITEM_EVERY):
                index = (f - delta) // NEW_ITEM_EVERY
                if index < 0:
                    break
                done = (f - index * NEW_ITEM_EVERY) / ITEM_DURATION
                if index < len(gold_items):
                    animating.append((index, done))

            return stage, (done_index, animating)

    def draw(self):
        global background
        self.image(background, 0, 0)

        stage, data = self.calc_stage()

        if stage == "silver":
            offsets_done, letters_done = data

            if offsets_done == int(offsets_done):
                # draw done letters on background
                background.begin_draw()
                offset = offsets[int(offsets_done) - 1]
                dr, dc = offset
                for r, c in silver_items[offset]:
                    for i in range(4):
                        background.fill(*SILVER_DARK)
                        background.text(
                            lines[r + i * dr][c + i * dc],
                            PADDING + c * W + i * dc * W,
                            PADDING + r * LEADING + i * dr * LEADING,
                        )
                background.end_draw()

            offset = offsets[int(offsets_done)]
            dr, dc = offset

            xylines = silver_lines[offset]
            xylines[:, 2] = xylines[:, 0] + min(letters_done, 3.3) * dc * W
            xylines[:, 3] = xylines[:, 1] + min(letters_done, 3.3) * dr * LEADING
            self.stroke_weight(FONT_SIZE)
            self.stroke(*SILVER, 48)
            self.lines(xylines)

            for r, c in silver_items[offset]:
                for i in range(4):
                    if i > letters_done:
                        break
                    alpha = int(255 * min(1.0, letters_done - i))
                    self.fill(*SILVER, alpha)
                    self.text(
                        lines[r + i * dr][c + i * dc],
                        PADDING + c * W + i * dc * W,
                        PADDING + r * LEADING + i * dr * LEADING,
                    )
        elif stage == "gold":
            (done_index, animating) = data
            if done_index is not None:
                # draw gold letters on background
                r, c = gold_items[done_index]
                background.begin_draw()
                background.fill(*GOLD_DARK)
                background.text(
                    lines[r][c],
                    PADDING + c * W,
                    PADDING + r * LEADING,
                )
                for dr in (-1, 1):
                    for dc in (-1, 1):
                        background.text(
                            lines[r + dr][c + dc],
                            PADDING + c * W + dc * W,
                            PADDING + r * LEADING + dr * LEADING,
                        )
                background.end_draw()

            self.stroke_weight(FONT_SIZE)
            self.stroke(*GOLD, 48)

            for index, done in animating:
                r, c = gold_items[index]
                alpha = int(
                    255 * min(1.0, 2 * done if done < 0.8 else 1 - 3 * (done - 0.8))
                )
                self.fill(*GOLD, alpha)
                self.text(
                    lines[r][c],
                    PADDING + c * W,
                    PADDING + r * LEADING,
                )
                if 2 * done > 0:
                    for dr in (-1, 1):
                        for dc in (-1, 1):
                            self.text(
                                lines[r + dr][c + dc],
                                PADDING + c * W + dc * W,
                                PADDING + r * LEADING + dr * LEADING,
                            )
                x0, y0 = gold_lines_start[index, :]
                extent = min(1.1, 2 * done)
                x1, y1 = x0 - extent * W, y0 - extent * LEADING
                x2, y2 = x0 + extent * W, y0 + extent * LEADING
                self.line(x1, y1, x2, y2)
                x1, y1 = x0 - extent * W, y0 + extent * LEADING
                x2, y2 = x0 + extent * W, y0 - extent * LEADING
                self.line(x1, y1, x2, y2)
