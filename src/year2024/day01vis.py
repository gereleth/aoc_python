# Problem statement: https://adventofcode.com/2024/day/1

import numpy as np
from py5 import Sketch
from aocd import get_data

from .day01 import day_title, parse_input

WIDTH = 1920
HEIGHT = 1080
PADDING = 40
SILVER = (153, 153, 204)
GOLD = (230, 230, 94)
TEXT_COLOR = (204, 204, 204)
BACKGROUND = (15, 15, 35)
LINES_COLOR = (75, 75, 90)
WHITE = (255, 255, 255)

text_input = get_data(year=2024, day=1, block=True)

list1, list2 = parse_input(text_input)
list1, list2 = np.array(list1), np.array(list2)
isin1 = np.isin(list2, list1)
N = len(list1)
dy = (HEIGHT - 2 * PADDING) / (N)
M = max(*list1, *list2)
dx = (WIDTH / 2 - PADDING * 1.5) / M
lines1 = np.zeros((N, 4))
lines2 = np.zeros((N, 4))

lines1[:, 0] = PADDING
lines1[:, 1] = PADDING + np.arange(N) * dy
lines1[:, 2] = PADDING + dx * list1
lines1[:, 3] = lines1[:, 1]

lines2[:, 0] = WIDTH / 2 + PADDING / 2
lines2[:, 1] = PADDING + np.arange(N) * dy
lines2[:, 2] = WIDTH / 2 + PADDING / 2 + dx * list2
lines2[:, 3] = lines2[:, 1]

idx1 = np.argsort(list1)
idx2 = np.argsort(list2)

sortedlines1 = lines1.copy()
sortedlines2 = lines2.copy()
sortedlines1[idx1, 1] = lines1[:, 1]
sortedlines1[:, 3] = sortedlines1[:, 1]
sortedlines2[idx2, 1] = lines2[:, 1]
sortedlines2[:, 3] = sortedlines2[:, 1]
goldlines2 = sortedlines2.copy()
goldlines2[~isin1, 2] = goldlines2[~isin1, 0]

delta = lines1.copy()
delta[:, 0] = PADDING + dx * np.minimum(list1[idx1], list2[idx2])
delta[:, 2] = PADDING + dx * np.maximum(list1[idx1], list2[idx2])
delta_moved = delta.copy()
delta_moved[:, 2] = WIDTH / 2 - PADDING / 2
delta_moved[:, 0] = delta[:, 0] + delta_moved[:, 2] - delta[:, 2]

stages = [
    # (name, duration, pause)
    ("init", 60, 0),
    ("sort", 60, 30),
    ("fly-left", 60, 0),
    ("compare-silver", 240, 30),
    ("fly-right", 60, 0),
    ("fly-delta", 60, 0),
    ("compare-gold", 240, 30),
    ("fade", 60, 0),
    ("final", -1, 0),
]


def get_stage(frame_count):
    start = 0
    for name, duration, pause in stages:
        if duration < 0:
            return name, 0.0
        if frame_count > start + duration + pause:
            start += duration + pause
            continue
        elif frame_count < start + duration:
            return name, (frame_count - start) / duration
        else:
            return name, 1.0


started = False
start_frame = 0


class VisSketch(Sketch):
    def settings(self):
        self.size(WIDTH, HEIGHT)
        self.smooth()

    def setup(self):
        self.stroke_weight(1)
        self.rect_mode(self.CENTER)
        self.stroke("white")
        self.window_title(f"Advent of Code 2024 - Day 1 - {day_title}")

    def mouse_clicked(self):
        global started, start_frame
        started = True
        start_frame = self.frame_count

    def draw(self):
        self.background(*BACKGROUND)
        if started:
            stage, share_done = get_stage(self.frame_count - start_frame)
        else:
            stage, share_done = get_stage(0)
        if stage == "init":
            self.stroke(*LINES_COLOR)
            self.lines(lines1)
            self.lines(lines2)
        elif stage == "sort":
            self.stroke(*LINES_COLOR)
            self.lines(lines1 * (1 - share_done) + share_done * sortedlines1)
            self.lines(lines2 * (1 - share_done) + share_done * sortedlines2)
        elif stage == "fly-left":
            self.stroke(*WHITE, 64)
            self.lines(sortedlines1)
            self.lines(
                sortedlines2
                - np.array(
                    [
                        share_done * (M * dx + PADDING),
                        0,
                        share_done * (M * dx + PADDING),
                        0,
                    ]
                )
            )
        elif stage == "compare-silver":
            self.stroke(*WHITE, 64)
            self.lines(sortedlines1)
            self.lines(
                sortedlines2 - np.array([M * dx + PADDING, 0, M * dx + PADDING, 0])
            )
            self.stroke(*SILVER)
            self.lines(delta[: int(N * share_done), :])
        elif stage == "fly-right":
            self.stroke(*WHITE, 64)
            self.lines(sortedlines1)
            self.lines(
                sortedlines2
                - np.array(
                    [
                        (1 - share_done) * (M * dx + PADDING),
                        0,
                        (1 - share_done) * (M * dx + PADDING),
                        0,
                    ]
                )
            )
            self.stroke(*SILVER)
            self.lines(delta)
        elif stage == "fly-delta":
            self.stroke(*LINES_COLOR)
            self.lines(sortedlines1)
            self.lines(sortedlines2)
            self.stroke(*SILVER)
            self.lines(delta * (1 - share_done) + delta_moved * share_done)
        elif stage == "compare-gold":
            self.stroke(*LINES_COLOR)
            self.lines(sortedlines1)
            self.lines(sortedlines2)
            self.stroke(*SILVER)
            self.lines(delta_moved)
            self.stroke(*GOLD)
            i = int((N - 1) * share_done)
            self.line(*sortedlines1[idx1[i], :])
            self.lines(goldlines2[idx2[: i + 1], :])
        elif stage == "fade":
            self.stroke(*WHITE, int(64 * (1 - share_done)))
            self.lines(sortedlines1)
            self.lines(sortedlines2)
            self.stroke(*SILVER)
            self.lines(delta_moved)
            self.stroke(*GOLD)
            self.lines(goldlines2[idx2, :])
        elif stage == "final":
            self.stroke(*SILVER)
            self.lines(delta_moved)
            self.stroke(*GOLD)
            self.lines(goldlines2[idx2, :])
