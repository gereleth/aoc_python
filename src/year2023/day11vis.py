# Problem statement: https://adventofcode.com/2023/day/11

import sys
import time
from aocd import get_data
import pygame as pg
from year2023.day11 import example_input

SILVER = (153, 153, 204)
GOLD = (230, 230, 94)
TEXT_COLOR = (204, 204, 204)
GREY_COLOR = (64, 64, 64)
BACKGROUND = (15, 15, 35, 255)
BACKGROUND_2 = (25, 25, 55)

WIDTH = 1280
HEIGHT = 720
W_PADDING = 50

FPS = 10
INITIAL_DELAY = 0.5
FONT_SIZE = 20


class ExpandingUniverseVis:
    def __init__(self, text):
        self.lines = text.split("\n")
        # locate galaxies
        single_line = "".join(self.lines)
        idx = [i for i, char in enumerate(single_line) if char == "#"]
        C = len(self.lines[0])
        self.galaxies = [(i // C, i % C) for i in idx]
        # precalculate expansions along rows
        expansions = 0
        self.exp_r = [0]
        self.expanded_rows = []
        for r, line in enumerate(self.lines):
            if all(char != "#" for char in line):
                expansions += 1
                self.expanded_rows.append(r)
            self.exp_r.append(expansions)
        # precalculate expansions along columns
        expansions = 0
        self.exp_c = [0]
        self.expanded_cols = []
        for c in range(C):
            if all(line[c] != "#" for line in self.lines):
                expansions += 1
                self.expanded_cols.append(c)
            self.exp_c.append(expansions)

    def galaxy_pairs(self):
        for a, pos_a in enumerate(self.galaxies[:-1]):
            for pos_b in self.galaxies[a + 1 :]:
                yield pos_a, pos_b

    def get_rect(self, r, c, expansion_factor):
        middlec = (self.exp_c[-1] * (expansion_factor - 1) + len(self.exp_c) - 1) / 2
        middler = (self.exp_r[-1] * (expansion_factor - 1) + len(self.exp_r) - 1) / 2
        left = c + (expansion_factor - 1) * self.exp_c[c] - middlec
        right = c + 1 + (expansion_factor - 1) * self.exp_c[c + 1] - middlec
        top = r + (expansion_factor - 1) * self.exp_r[r] - middler
        bottom = r + 1 + (expansion_factor - 1) * self.exp_r[r + 1] - middler
        return (left, top, right - left, bottom - top)

    def get_width(self, expansion_factor):
        return len(self.exp_c) - 1 + self.exp_c[-1] * expansion_factor

    def get_height(self, expansion_factor):
        return len(self.exp_r) - 1 + self.exp_r[-1] * expansion_factor


def run():
    # Get sizes from input data
    # text_input = get_data(year=2023, day=11)
    text_input = example_input
    universe = ExpandingUniverseVis(text_input)
    # print(len(universe.exp_c), len(universe.exp_r))
    R = len(universe.lines)
    C = len(universe.lines[0])
    RE = universe.get_height(3)
    CE = universe.get_width(3)
    unit = min(0.90 * WIDTH / CE, 0.90 * HEIGHT / RE)

    WP = (WIDTH - unit * CE) / 2
    HP = (HEIGHT - unit * RE) / 2
    WP = min(WP, HP)
    HP = WP

    WU = CE * unit
    HU = RE * unit

    def xpixels(c):
        return WP + WU / 2 + unit * c

    def ypixels(r):
        return HP + HU / 2 + unit * r

    pg.init()
    screen = pg.display.set_mode([WIDTH, HEIGHT])
    pg.display.set_caption("Advent of Code 2023 - Day 11 - Cosmic Expansion")

    clock = pg.time.Clock()

    t0 = time.perf_counter()
    t = 0
    print(universe.exp_c)
    print(universe.get_rect(0, 3, 1))
    print(universe.get_rect(0, 3, 1.1))
    print(universe.get_rect(0, 3, 2))
    print(universe.get_rect(0, 3, 3))
    running = True
    # main loop
    while running:
        clock.tick(FPS)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                t0 = time.perf_counter()  # reset to start

        t = max(0, time.perf_counter() - t0 - INITIAL_DELAY)
        expansion_factor = min(3, 1 + 2 * t / 5)

        # erase everything
        screen.fill(BACKGROUND)

        # draw expanded rows
        for r in universe.expanded_rows:
            (left, top, w, h) = universe.get_rect(r, 0, expansion_factor)
            x0 = xpixels(left)
            y0 = ypixels(top)
            y1 = ypixels(top + h)
            (left, top, w, h) = universe.get_rect(r, C - 1, expansion_factor)
            x1 = xpixels(left + w)
            rect = pg.Rect(x0, y0, x1 - x0, y1 - y0)
            pg.draw.rect(screen, BACKGROUND_2, rect)
        # draw expanded columns
        for c in universe.expanded_cols:
            (left, top, w, h) = universe.get_rect(0, c, expansion_factor)
            y0 = ypixels(top)
            x0 = xpixels(left)
            x1 = xpixels(left + w)
            (left, top, w, h) = universe.get_rect(R - 1, c, expansion_factor)
            y1 = ypixels(top + h)
            rect = pg.Rect(x0, y0, x1 - x0, y1 - y0)
            pg.draw.rect(screen, BACKGROUND_2, rect)
        # draw galaxies
        for pos in universe.galaxies:
            (left, top, w, h) = universe.get_rect(*pos, expansion_factor)
            pg.draw.circle(
                screen,
                GOLD,
                (xpixels(left + w / 2), ypixels(top + h / 2)),
                max(5, unit * 0.5),
            )
        # draw horizontal grid lines
        for r in range(R):
            (left, top, w, h) = universe.get_rect(r, 0, expansion_factor)
            y0 = ypixels(top)
            x0 = xpixels(left)
            (left, top, w, h) = universe.get_rect(r, C - 1, expansion_factor)
            x1 = xpixels(left + w)
            y1 = ypixels(top + h)
            pg.draw.line(screen, SILVER, (x0, y0), (x1, y0))
        pg.draw.line(screen, SILVER, (x0, y1), (x1, y1))
        # draw vertical grid lines
        for c in range(C):
            (left, top, w, h) = universe.get_rect(0, c, expansion_factor)
            x0 = xpixels(left)
            y0 = ypixels(top)
            (left, top, w, h) = universe.get_rect(R - 1, c, expansion_factor)
            y1 = ypixels(top + h)
            x1 = xpixels(left + w)
            pg.draw.line(screen, SILVER, (x0, y0), (x0, y1))
        pg.draw.line(screen, SILVER, (x1, y0), (x1, y1))

        # actually update the screen now
        pg.display.flip()

    pg.quit()
    sys.exit()


if __name__ == "__main__":
    run()
