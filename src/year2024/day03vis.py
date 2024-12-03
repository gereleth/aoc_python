# Problem statement: https://adventofcode.com/2024/day/3

import re
from py5 import Sketch, Py5Font
from aocd import get_data

from .day03 import day_title

# print(Py5Font.list()) # list available fonts

WIDTH = 1920
HEIGHT = 1080
PADDING = 100
SILVER = (153, 153, 204)
GOLD = (230, 230, 94)
TEXT_COLOR = (204, 204, 204)
BACKGROUND = (15, 15, 35)
BACKGROUND_2 = (25, 25, 55)
FADED_COLOR = (75, 75, 90)
TEXT_COLOR = (204, 204, 204)
WHITE = (255, 255, 255)

INITIAL_DELAY = 0
FRAMES_PER_TURN = 15
GOLD_DELAY = 7

text = get_data(year=2024, day=3, block=True)
text = "".join(text.split("\n"))
expr = re.compile(r"(mul\(\d{1,3},\d{1,3}\)|do\(\)|don\'t\(\))")
spans = []
start = 0
enabled = True
for match in re.finditer(expr, text):
    span = dict(text=match.group(), kind="mult", enabled=enabled)
    if match.start() > start:
        spans.append(dict(text=text[start : match.start()], kind="garbage"))
    if span["text"] == "do()":
        enabled = True
        span["kind"] = "do"
    elif span["text"] == "don't()":
        span["kind"] = "dont"
        enabled = False
    spans.append(span)
    start = match.end()
if start < len(text):
    spans.append(dict(text=text[start:], kind="garbage"))

lines = [[spans[0]]]
start = len(spans[0])
for span in spans[1:]:
    if start + len(span["text"]) < 80:
        lines[-1].append(span)
        start += len(span["text"])
    else:
        lines.append([span])
        start = len(span["text"])

totals_1 = [0]
totals_2 = [0]
t1 = 0
t2 = 0
for line in lines:
    for span in line:
        if span["kind"] != "mult":
            continue
        a, b = re.findall(r"(\d+)", span["text"])
        t1 += int(a) * int(b)
        if span["enabled"]:
            t2 += int(a) * int(b)
    totals_1.append(t1)
    totals_2.append(t2)

# print(lines[:10])

started = False
start_frame = 0

FONT_SIZE = 25
LEADING = 50  # line height
W = 30  # single letter width


total_1 = 0
total_2 = 0


class VisSketch(Sketch):
    def settings(self):
        self.size(WIDTH, HEIGHT)
        self.smooth()

    def setup(self):
        self.stroke_weight(1)
        self.stroke("white")
        self.window_title(f"Advent of Code 2024 - Day 3 - {day_title}")
        font = self.create_font("Liberation Mono", FONT_SIZE)
        self.text_font(font)
        # self.text_leading(LEADING)
        global W
        W = self.text_width("w")

    def mouse_clicked(self):
        global started, start_frame
        started = True
        start_frame = self.frame_count

    def draw_silver_line(self, line, y):
        start = 0
        for s, span in enumerate(line):
            if span["kind"] == "mult":
                self.no_stroke()
                self.fill(*BACKGROUND_2)
                self.rect(
                    PADDING + W * start - 1,
                    y - LEADING / 2 - FONT_SIZE / 2 + 8,
                    W * len(span["text"]),
                    LEADING - 8,
                )
                self.fill(*SILVER)
            else:
                self.fill(*FADED_COLOR)
            self.text(span["text"], PADDING + W * start, y)
            start += len(span["text"])

    def draw_gold_line(self, line, y):
        start = 0
        for s, span in enumerate(line):
            if span["kind"] == "garbage":
                self.fill(*FADED_COLOR)
            elif span["kind"] == "mult":
                self.no_stroke()
                self.fill(*BACKGROUND_2)
                self.rect(
                    PADDING + W * start - 1,
                    y - LEADING / 2 - FONT_SIZE / 2 + 8,
                    W * len(span["text"]),
                    LEADING - 8,
                )
                if span["enabled"]:
                    self.fill(*GOLD)
                else:
                    self.fill(*GOLD, 64)
            elif span["kind"] == "dont":
                self.stroke(*GOLD)
                self.no_fill()
                self.rect(
                    PADDING + W * start - 1,
                    y - LEADING / 2 - FONT_SIZE / 2 + 8,
                    W * len(span["text"]),
                    LEADING - 8,
                )
                self.fill(*GOLD)
            elif span["kind"] == "do":
                self.stroke(*GOLD)
                self.fill(*GOLD)
                self.rect(
                    PADDING + W * start - 1,
                    y - LEADING / 2 - FONT_SIZE / 2 + 4,
                    W * len(span["text"]),
                    LEADING,
                )
                self.fill(*BACKGROUND)
            self.text(span["text"], PADDING + W * start, y)
            start += len(span["text"])

    def draw_raw_line(self, line, y):
        start = 0
        self.fill(*TEXT_COLOR)
        for s, span in enumerate(line):
            self.text(span["text"], PADDING + W * start, y)
            start += len(span["text"])

    def draw(self):
        global total_1, total_2
        self.background(*BACKGROUND)
        if started:
            turn = max(0, self.frame_count - start_frame) // FRAMES_PER_TURN
            dturn = (
                max(0, self.frame_count - start_frame) % FRAMES_PER_TURN
            ) / FRAMES_PER_TURN
        else:
            turn = 0
            dturn = 0

        silver_lines = min(len(lines) + 1, turn)
        gold_lines = min(len(lines) + 1, max(0, turn - GOLD_DELAY))
        max_scroll = (len(lines)) * LEADING - HEIGHT + PADDING + 100
        scrolled = min(
            max(0, silver_lines - 14) * LEADING,
            max_scroll,
        )

        dh = 0
        if scrolled > 0 and scrolled < max_scroll:
            dh = dturn * LEADING

        for i, line in enumerate(lines):
            y = PADDING - scrolled - dh + i * LEADING
            if y < -LEADING or y > HEIGHT:
                continue
            if i < gold_lines:
                self.draw_gold_line(line, y)
            elif i < silver_lines:
                self.draw_silver_line(line, y)
            else:
                self.draw_raw_line(line, y)

        # render totals
        self.fill(*SILVER)
        s = min(len(lines), silver_lines)
        offsety = PADDING - scrolled + (silver_lines - 1) * LEADING
        if scrolled == 0 and silver_lines > 0:
            offsety += dturn * LEADING - LEADING
        elif scrolled == max_scroll and silver_lines <= len(lines):
            offsety += dturn * LEADING - LEADING
        # print(
        #     f"t{turn}",
        #     f"dt{int(dturn * 100)}",
        #     f"s{silver_lines}",
        #     f"scr{scrolled}",
        #     f"y{offsety}",
        #     sep="\t",
        # )
        self.text(f"> {totals_1[s]}", PADDING + 85 * W, offsety)

        self.fill(*GOLD)
        g = min(len(lines), gold_lines)
        offsety = PADDING - scrolled + (gold_lines - 1) * LEADING
        if (scrolled == 0 and gold_lines > 0) or (
            scrolled == max_scroll and gold_lines < len(lines)
        ):
            offsety += dturn * LEADING - LEADING
        # print(silver_lines, gold_lines)
        if gold_lines == silver_lines:
            offsety -= LEADING
        self.text(
            f"> {totals_2[g]}",
            PADDING + 85 * W,
            offsety,
        )
