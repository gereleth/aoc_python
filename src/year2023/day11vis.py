# Problem statement: https://adventofcode.com/2023/day/11

import sys
import time
from aocd import get_data
import pygame as pg
from year2023.day11 import example_input

SILVER = (153, 153, 204)
GOLD = (230, 230, 94)
TEXT_COLOR = (204, 204, 204)
GRID_COLOR = (100, 100, 100)
BACKGROUND = (15, 15, 35, 255)
BACKGROUND_2 = (25, 25, 55)

WIDTH = 1280
HEIGHT = 720
W_PADDING = 50

FPS = 10
INITIAL_DELAY = 0.5
EXPANSION_TIME = 1
PATH_DELAY = 0.5
TIME_PER_PATH = 5
FONT_SIZE = 20
TOTAL_FONT_SIZE = 30


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
    font = pg.font.SysFont("monospace", FONT_SIZE)
    totals_font = pg.font.SysFont("monospace", TOTAL_FONT_SIZE)

    clock = pg.time.Clock()

    t0 = time.perf_counter()
    t = 0

    galaxy_pairs = list(universe.galaxy_pairs())

    # prepare step counter symbols
    long_step_symbol = pg.Surface((3 * unit, unit))
    pg.draw.rect(long_step_symbol, BACKGROUND_2, pg.Rect(0, 0, 3 * unit, unit))
    pg.draw.rect(long_step_symbol, GRID_COLOR, pg.Rect(0, 0, 3 * unit, unit), 2)

    short_step_symbol = pg.Surface((unit, unit))
    pg.draw.rect(short_step_symbol, BACKGROUND, pg.Rect(0, 0, unit, unit))
    pg.draw.rect(short_step_symbol, GRID_COLOR, pg.Rect(0, 0, unit, unit), 2)

    long_steps = 0
    short_steps = 0
    total1 = 0
    total2 = 0

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
        expansion_factor = min(3, 1 + 2 * t / EXPANSION_TIME)
        path_t = min(
            len(galaxy_pairs) - 1, (t - EXPANSION_TIME - PATH_DELAY) / TIME_PER_PATH
        )
        path_index = int(path_t)
        path_pct = path_t - path_index

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
            pg.draw.line(screen, GRID_COLOR, (x0, y0), (x1, y0))
        pg.draw.line(screen, GRID_COLOR, (x0, y1), (x1, y1))
        # draw vertical grid lines
        for c in range(C):
            (left, top, w, h) = universe.get_rect(0, c, expansion_factor)
            x0 = xpixels(left)
            y0 = ypixels(top)
            (left, top, w, h) = universe.get_rect(R - 1, c, expansion_factor)
            y1 = ypixels(top + h)
            x1 = xpixels(left + w)
            pg.draw.line(screen, GRID_COLOR, (x0, y0), (x0, y1))
        pg.draw.line(screen, GRID_COLOR, (x1, y0), (x1, y1))

        if t > EXPANSION_TIME + PATH_DELAY:
            # draw paths
            (ra, ca), (rb, cb) = galaxy_pairs[path_index]
            (la, ta, w, h) = universe.get_rect(ra, ca, expansion_factor)
            (lb, tb, w, h) = universe.get_rect(rb, cb, expansion_factor)
            xa, xb = xpixels(la + w / 2), xpixels(lb + w / 2)
            ya, yb = ypixels(ta + h / 2), ypixels(tb + h / 2)
            pg.draw.line(screen, GOLD, (xa, ya), (xa, yb), 4)
            pg.draw.line(screen, GOLD, (xa, yb), (xb, yb), 4)

            # draw counts
            short_step_count = font.render(str(short_steps) + " ", 1, TEXT_COLOR)
            short_step_count_rect = short_step_count.get_rect(
                centery=HEIGHT / 2, left=0.6 * WIDTH
            )
            screen.blit(short_step_count, short_step_count_rect)
            short_step_symbol_rect = short_step_symbol.get_rect(
                centery=HEIGHT / 2, left=short_step_count_rect.right
            )
            screen.blit(short_step_symbol, short_step_symbol_rect)
            long_step_count = font.render(" + " + str(long_steps) + " ", 1, TEXT_COLOR)
            long_step_count_rect = long_step_count.get_rect(
                centery=HEIGHT / 2, left=short_step_symbol_rect.right
            )
            screen.blit(long_step_count, long_step_count_rect)
            long_step_symbol_rect = long_step_symbol.get_rect(
                centery=HEIGHT / 2, left=long_step_count_rect.right
            )
            screen.blit(long_step_symbol, long_step_symbol_rect)
            # distance path totals
            silver_distance = short_steps + 2 * long_steps
            silver_distance_text = font.render(" = " + str(silver_distance), 1, SILVER)
            silver_distance_rect = silver_distance_text.get_rect(
                bottom=HEIGHT / 2, left=long_step_symbol_rect.right
            )
            screen.blit(silver_distance_text, silver_distance_rect)
            gold_distance = short_steps + 1_000_000 * long_steps
            gold_distance_text = font.render(" = " + str(gold_distance), 1, GOLD)
            gold_distance_rect = gold_distance_text.get_rect(
                top=HEIGHT / 2, left=long_step_symbol_rect.right
            )
            screen.blit(gold_distance_text, gold_distance_rect)
            # part running totals
            total1_label_text = totals_font.render("Part 1:", 1, SILVER)
            total1_label_rect = total1_label_text.get_rect(
                centery=HEIGHT / 4, right=long_step_symbol_rect.right
            )
            screen.blit(total1_label_text, total1_label_rect)
            total1_value_text = totals_font.render(" " + str(total1), 1, SILVER)
            total1_value_rect = total1_value_text.get_rect(
                centery=HEIGHT / 4, left=long_step_symbol_rect.right
            )
            screen.blit(total1_value_text, total1_value_rect)
            total2_label_text = totals_font.render("Part 2:", 1, GOLD)
            total2_label_rect = total2_label_text.get_rect(
                centery=HEIGHT * 3 / 4, right=long_step_symbol_rect.right
            )
            screen.blit(total2_label_text, total2_label_rect)
            total2_value_text = totals_font.render(" " + str(total2), 1, GOLD)
            total2_value_rect = total2_value_text.get_rect(
                centery=HEIGHT * 3 / 4, left=long_step_symbol_rect.right
            )
            screen.blit(total2_value_text, total2_value_rect)
        # actually update the screen now
        pg.display.flip()

    pg.quit()
    sys.exit()


if __name__ == "__main__":
    run()
