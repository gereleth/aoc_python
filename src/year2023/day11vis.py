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

FPS = 60
INITIAL_DELAY = 2

START_EXPANSION_AFTER = 2
EXPANSION_TIME = 2
PATH_DELAY = 1
NUM_SLOW_PATHS = 4  # how many paths to animate slowly
PATH_SPEED_SLOW = 2  # units per second for slow path animation
PATH_SPEED_FAST = 25  # units per second for fast path animation
PAUSE_BETWEEN_PATHS = 1  # seconds of pause between paths
FONT_SIZE = 20
TOTAL_FONT_SIZE = 30

TOTALS_POS_LEFT = 0.65 * WIDTH


class ExpandingUniverseVis:
    def __init__(self, text):
        self.lines = text.split("\n")
        self.expansion_factor = 1
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

    def get_rect(self, r, c):
        middlec = (
            self.exp_c[-1] * (self.expansion_factor - 1) + len(self.exp_c) - 1
        ) / 2
        middler = (
            self.exp_r[-1] * (self.expansion_factor - 1) + len(self.exp_r) - 1
        ) / 2
        left = c + (self.expansion_factor - 1) * self.exp_c[c] - middlec
        right = c + 1 + (self.expansion_factor - 1) * self.exp_c[c + 1] - middlec
        top = r + (self.expansion_factor - 1) * self.exp_r[r] - middler
        bottom = r + 1 + (self.expansion_factor - 1) * self.exp_r[r + 1] - middler
        return (left, top, right - left, bottom - top)

    def get_width(self):
        return len(self.exp_c) - 1 + self.exp_c[-1] * self.expansion_factor

    def get_height(self):
        return len(self.exp_r) - 1 + self.exp_r[-1] * self.expansion_factor

    def get_path_lines(self, pos_a, pos_b, traveled_distance):
        lines = []
        (la, ta, w, h) = self.get_rect(*pos_a)
        (lb, tb, w, h) = self.get_rect(*pos_b)
        dc = abs(la - lb)
        dr = abs(ta - tb)
        traveled_r = min(traveled_distance, dr) * (1 if tb > ta else -1)
        c0 = la + w / 2
        c1 = lb + w / 2
        r0 = ta + h / 2
        r1 = tb + h / 2
        # vertical line goes first
        lines.append([(r0, c0), (r0 + traveled_r, c0)])
        # and horizontal line if we reached it
        if traveled_distance > dr:
            traveled_c = min(traveled_distance - dr, dc) * (1 if lb > la else -1)
            lines.append([(r1, c0), (r1, c0 + traveled_c)])
        return lines

    def get_path_waypoints(self, pos_a, pos_b, traveled_distance):
        waypoints = []
        (ra, ca), (rb, cb) = pos_a, pos_b
        distance = 0
        while ra != rb:
            ra += 1 if rb > ra else -1
            distance = self.get_distance((ra, ca), pos_a)
            if distance < traveled_distance:
                (l, t, w, h) = self.get_rect(ra, ca)
                waypoints.append((t + h / 2, l + w / 2, w != h))
            else:
                return waypoints
        while ca != cb:
            ca += 1 if cb > ca else -1
            distance = self.get_distance((ra, ca), pos_a)
            if distance < traveled_distance:
                (l, t, w, h) = self.get_rect(ra, ca)
                waypoints.append((t + h / 2, l + w / 2, w != h))
            else:
                break
        return waypoints

    def get_distance(self, pos_a, pos_b):
        (la, ta, wa, ha) = self.get_rect(*pos_a)
        (lb, tb, wb, hb) = self.get_rect(*pos_b)
        return abs(la + wa / 2 - lb - wb / 2) + abs(ta + ha / 2 - tb - hb / 2)


def run():
    # It doesn't really look good with real inputs :shrug:
    # text_input = get_data(year=2023, day=11)
    text_input = example_input
    universe = ExpandingUniverseVis(text_input)
    # print(len(universe.exp_c), len(universe.exp_r))
    R = len(universe.lines)
    C = len(universe.lines[0])
    universe.expansion_factor = 3
    RE = universe.get_height()
    CE = universe.get_width()
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
    d = 0
    distances = []  # collect visual distances for timing path animations
    for i, (a, b) in enumerate(galaxy_pairs):
        speed = PATH_SPEED_FAST if i >= NUM_SLOW_PATHS else PATH_SPEED_SLOW
        d += universe.get_distance(a, b) + speed * PAUSE_BETWEEN_PATHS
        distances.append(d)

    # prepare step counter symbols
    long_step_symbol = pg.Surface((3 * unit, unit))
    pg.draw.rect(long_step_symbol, BACKGROUND_2, pg.Rect(0, 0, 3 * unit, unit))
    pg.draw.rect(long_step_symbol, GRID_COLOR, pg.Rect(0, 0, 3 * unit, unit), 2)

    short_step_symbol = pg.Surface((unit, unit))
    pg.draw.rect(short_step_symbol, BACKGROUND, pg.Rect(0, 0, unit, unit))
    pg.draw.rect(short_step_symbol, GRID_COLOR, pg.Rect(0, 0, unit, unit), 2)

    path_index = 0
    long_steps = 0
    short_steps = 0
    total1 = 0
    total2 = 0
    silver_distance = 0
    gold_distance = 0
    totals_done = False
    last_t = 0
    total_traveled = 0

    running = True
    # main loop
    while running:
        clock.tick(FPS)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                t0 = time.perf_counter()  # reset to start
                universe.expansion_factor = 1
                path_index = 0
                totals_done = False
                total1 = 0
                total2 = 0
                total_traveled = 0
                last_t = 0

        t = max(0, time.perf_counter() - t0 - INITIAL_DELAY)
        universe.expansion_factor = min(
            3, 1 + 2 * max(0, t - START_EXPANSION_AFTER) / EXPANSION_TIME
        )
        dt = t - last_t
        last_t = t
        if t > START_EXPANSION_AFTER + EXPANSION_TIME + PATH_DELAY:
            speed = PATH_SPEED_FAST if path_index >= NUM_SLOW_PATHS else PATH_SPEED_SLOW
            total_traveled += dt * speed
        if total_traveled > distances[path_index]:
            if path_index < len(galaxy_pairs) - 1:
                total1 += silver_distance
                total2 += gold_distance
                path_index += 1
            elif not totals_done:
                totals_done = True
                total1 += silver_distance
                total2 += gold_distance
        path_traveled = total_traveled - (
            0 if path_index == 0 else distances[path_index - 1]
        )

        # erase everything
        screen.fill(BACKGROUND)

        # draw expanded rows
        if t > START_EXPANSION_AFTER:
            for r in universe.expanded_rows:
                (left, top, w, h) = universe.get_rect(r, 0)
                x0 = xpixels(left)
                y0 = ypixels(top)
                y1 = ypixels(top + h)
                (left, top, w, h) = universe.get_rect(r, C - 1)
                x1 = xpixels(left + w)
                rect = pg.Rect(x0, y0, x1 - x0, y1 - y0)
                pg.draw.rect(screen, BACKGROUND_2, rect)
            # draw expanded columns
            for c in universe.expanded_cols:
                (left, top, w, h) = universe.get_rect(0, c)
                y0 = ypixels(top)
                x0 = xpixels(left)
                x1 = xpixels(left + w)
                (left, top, w, h) = universe.get_rect(R - 1, c)
                y1 = ypixels(top + h)
                rect = pg.Rect(x0, y0, x1 - x0, y1 - y0)
                pg.draw.rect(screen, BACKGROUND_2, rect)
        # draw galaxies
        for pos in universe.galaxies:
            (left, top, w, h) = universe.get_rect(*pos)
            pg.draw.circle(
                screen,
                GOLD
                if (total_traveled > 0 and pos in galaxy_pairs[path_index])
                else SILVER,
                (xpixels(left + w / 2), ypixels(top + h / 2)),
                max(5, unit * 0.5),
                # 0 if (total_traveled > 0 and pos in galaxy_pairs[path_index]) else 6,
            )
        # draw horizontal grid lines
        for r in range(R):
            (left, top, w, h) = universe.get_rect(r, 0)
            y0 = ypixels(top)
            x0 = xpixels(left)
            (left, top, w, h) = universe.get_rect(r, C - 1)
            x1 = xpixels(left + w)
            y1 = ypixels(top + h)
            pg.draw.line(screen, GRID_COLOR, (x0, y0), (x1, y0))
        pg.draw.line(screen, GRID_COLOR, (x0, y1), (x1, y1))
        # draw vertical grid lines
        for c in range(C):
            (left, top, w, h) = universe.get_rect(0, c)
            x0 = xpixels(left)
            y0 = ypixels(top)
            (left, top, w, h) = universe.get_rect(R - 1, c)
            y1 = ypixels(top + h)
            x1 = xpixels(left + w)
            pg.draw.line(screen, GRID_COLOR, (x0, y0), (x0, y1))
        pg.draw.line(screen, GRID_COLOR, (x1, y0), (x1, y1))

        if t > START_EXPANSION_AFTER + EXPANSION_TIME:
            # draw paths
            pos_a, pos_b = galaxy_pairs[path_index]
            lines = universe.get_path_lines(pos_a, pos_b, path_traveled)
            for (r0, c0), (r1, c1) in lines:
                x0, y0 = xpixels(c0), ypixels(r0)
                x1, y1 = xpixels(c1), ypixels(r1)
                pg.draw.line(screen, BACKGROUND_2, (x0, y0), (x1, y1), 4)
                pg.draw.line(screen, SILVER, (x0, y0), (x1, y1), 2)
            # draw waypoints
            waypoints = universe.get_path_waypoints(pos_a, pos_b, path_traveled)
            short_steps = 0
            long_steps = 0
            silver_distance = 0
            gold_distance = 0
            for r, c, is_expanded in waypoints:
                x, y = xpixels(c), ypixels(r)
                pg.draw.circle(screen, BACKGROUND_2, (x, y), 7)
                pg.draw.circle(screen, SILVER, (x, y), 6)
                short_steps += not is_expanded
                long_steps += is_expanded
            # draw counts
            short_step_count = font.render(str(short_steps) + " ", 1, TEXT_COLOR)
            short_step_count_rect = short_step_count.get_rect(
                centery=HEIGHT / 2, right=TOTALS_POS_LEFT
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
                centery=HEIGHT / 4, left=TOTALS_POS_LEFT
            )
            screen.blit(total1_label_text, total1_label_rect)
            total1_value_text = totals_font.render(" " + str(total1), 1, SILVER)
            total1_value_rect = total1_value_text.get_rect(
                centery=HEIGHT / 4, left=total1_label_rect.right
            )
            screen.blit(total1_value_text, total1_value_rect)
            total2_label_text = totals_font.render("Part 2:", 1, GOLD)
            total2_label_rect = total2_label_text.get_rect(
                centery=HEIGHT * 3 / 4, left=TOTALS_POS_LEFT
            )
            screen.blit(total2_label_text, total2_label_rect)
            total2_value_text = totals_font.render(" " + str(total2), 1, GOLD)
            total2_value_rect = total2_value_text.get_rect(
                centery=HEIGHT * 3 / 4, left=total2_label_rect.right
            )
            screen.blit(total2_value_text, total2_value_rect)
        # actually update the screen now
        pg.display.flip()

    pg.quit()
    sys.exit()


if __name__ == "__main__":
    run()
