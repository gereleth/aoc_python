# Problem statement: https://adventofcode.com/2023/day/14

import sys
import time
from aocd import get_data
import pygame as pg
from year2023.day14 import example_input
from itertools import cycle

SILVER = (153, 153, 204)
GOLD = (230, 230, 94)
TEXT_COLOR = (204, 204, 204)
RED = (255, 120, 120)
WHITE = (255, 255, 255)
GRID_COLOR = (100, 100, 100)
BACKGROUND = (15, 15, 35, 255)
BACKGROUND_2 = (25, 25, 55)

WIDTH = 1280
HEIGHT = 720
W_PADDING = 50

FPS = 60
INITIAL_DELAY = 2
PAUSE_BETWEEN_ROLLS = 0.5
LOAD_CALC_TIME = 5

FONT_SIZE = 20
TOTAL_FONT_SIZE = 30
TOTALS_POS_LEFT = 20
EPS = 0.001
GRAVITY = 50


class RollingStone:
    def __init__(self, r, c):
        self.r = r  # where we are
        self.c = c
        self.r1 = r  # where we need to be
        self.c1 = c
        self.vr = 0  # current speed
        self.vc = 0
        self.marked = False

    def move(self, dt, gravity):
        dr = self.r - self.r1
        gr = 0
        if dr < -EPS:
            gr = gravity
        elif dr > EPS:
            gr = -gravity
        dc = self.c - self.c1
        gc = 0
        if dc < -EPS:
            gc = gravity
        elif dc > EPS:
            gc = -gravity
        if abs(gr) + abs(gc) == 0:
            self.r = self.r1
            self.c = self.c1
            self.vr = 0
            self.vc = 0
            return False
        vr = self.vr + dt * gr
        vc = self.vc + dt * gc
        moved_r = dt * (vr + self.vr) / 2
        moved_c = dt * (vc + self.vc) / 2
        self.vr = vr
        self.vc = vc
        if abs(moved_r) > abs(dr):
            moved_r = moved_r * abs(dr) / abs(moved_r)
            self.vr = 0
            self.r = self.r1
        else:
            self.r += moved_r
        if abs(moved_c) > abs(dc):
            moved_c = moved_c * abs(dc) / abs(moved_c)
            self.vc = 0
            self.c = self.c1
        else:
            self.c += moved_c
        return self.is_moving

    def set_destination(self, r, c):
        self.r1 = r
        self.c1 = c

    @property
    def is_moving(self):
        return (self.r != self.r1) or (self.c != self.c1)


class TiltPlatformVis:
    def __init__(self, text, maxwidth, maxheight):
        self.lines = []
        for r, line in enumerate(text.split("\n")):
            row = []
            for c, char in enumerate(line):
                if char == "O":
                    row.append(RollingStone(r, c))
                else:
                    row.append(char)
            self.lines.append(row)
        self.moving = set()
        # size up and prepare background
        self.maxwidth = maxwidth
        self.maxheight = maxheight
        self.R = len(self.lines)
        self.C = len(self.lines[0])
        self.unit = int(min(maxwidth / (self.C + 2), maxheight / (self.R + 2)))
        self.surface = pg.Surface(((self.C + 2) * self.unit, (self.R + 2) * self.unit))
        self.surface.fill(BACKGROUND)
        pg.draw.rect(
            self.surface,
            GRID_COLOR,
            pg.Rect(0, 0, (self.C + 2) * self.unit, (self.R + 2) * self.unit),
            self.unit,
        )
        for r, line in enumerate(self.lines):
            for c, char in enumerate(line):
                if char == "#":
                    pg.draw.rect(
                        self.surface,
                        GRID_COLOR,
                        pg.Rect(
                            self.unit * (c + 1),
                            self.unit * (r + 1),
                            self.unit,
                            self.unit,
                        ),
                    )
        self.background = self.surface.copy()
        self.load_color = None
        self.load_calc_time = -1
        self.load = 0
        self.load_row = -1
        self.cycle_number = 0
        self.direction = "N"
        self.period = -1
        self.period_start = -1
        self.last_seen_after = {}
        self.gist_imgs = []
        self.spin_cycle = cycle(
            (
                ("N", self.roll_north),
                ("W", self.roll_west),
                ("S", self.roll_south),
                ("E", self.roll_east),
            )
        )
        self.state = "paused"
        self.pause_left = 0
        self.PAUSE_BETWEEN_ROLLS = PAUSE_BETWEEN_ROLLS
        self.gravity = GRAVITY
        self.gold_done = False

    def update(self, dt):
        if self.state == "paused":
            if self.pause_left > 0:
                self.pause_left = max(0, self.pause_left - dt)
            else:
                self.do_next_thing()
        elif self.state == "tilt":
            still_moving = set()
            for r, c in self.moving:
                stone = self.lines[r][c]
                if stone.move(dt, self.gravity):
                    still_moving.add((r, c))
            self.moving = still_moving
            self.render()
            if len(self.moving) == 0:
                self.state = "paused"
                self.pause_left = self.PAUSE_BETWEEN_ROLLS
        elif self.state == "load":
            self.load_calc_time += dt
            self.load_row = min(
                self.R, round(self.R * 1.1 * self.load_calc_time / LOAD_CALC_TIME)
            )
            self.render()
            if self.load_calc_time > LOAD_CALC_TIME:
                self.load_row = -1
                self.do_next_thing()

    def calc_load(self, color=SILVER):
        self.state = "load"
        self.load_color = color
        self.load = 0
        self.load_calc_time = 0
        self.load_row = 0
        # actual calculation in self.update()

    def roll_north(self):
        for col in range(self.C):
            picked_up = []
            for row in range(self.R - 1, -1, -1):
                element = self.lines[row][col]
                if type(element) is RollingStone:
                    picked_up.append(element)
                    self.lines[row][col] = "."
                elif self.lines[row][col] == "#":
                    for r, stone in enumerate(reversed(picked_up)):
                        stone.r1 = row + r + 1
                        self.lines[row + r + 1][col] = stone
                        self.moving.add((row + r + 1, col))
                    picked_up.clear()
            for r, stone in enumerate(reversed(picked_up)):
                stone.r1 = r
                self.lines[r][col] = stone
                self.moving.add((r, col))
        return self

    def roll_south(self):
        for col in range(self.C):
            picked_up = []
            for row in range(self.R):
                element = self.lines[row][col]
                if type(element) is RollingStone:
                    picked_up.append(element)
                    self.lines[row][col] = "."
                elif self.lines[row][col] == "#":
                    for r, stone in enumerate(reversed(picked_up)):
                        stone.r1 = row - r - 1
                        self.lines[row - r - 1][col] = stone
                        self.moving.add((row - r - 1, col))
                    picked_up.clear()
            for r, stone in enumerate(reversed(picked_up)):
                stone.r1 = self.R - 1 - r
                self.lines[self.R - 1 - r][col] = stone
                self.moving.add((self.R - 1 - r, col))
        return self

    def roll_east(self):
        for row in range(self.R):
            picked_up = []
            for col in range(self.C):
                element = self.lines[row][col]
                if type(element) is RollingStone:
                    picked_up.append(element)
                    self.lines[row][col] = "."
                elif self.lines[row][col] == "#":
                    for r, stone in enumerate(reversed(picked_up)):
                        stone.c1 = col - r - 1
                        self.lines[row][col - r - 1] = stone
                        self.moving.add((row, col - r - 1))
                    picked_up.clear()
            for r, stone in enumerate(reversed(picked_up)):
                stone.c1 = self.C - r - 1
                self.lines[row][self.C - r - 1] = stone
                self.moving.add((row, self.C - r - 1))
        return self

    def roll_west(self):
        for row in range(self.R):
            picked_up = []
            for col in range(self.C - 1, -1, -1):
                element = self.lines[row][col]
                if type(element) is RollingStone:
                    picked_up.append(element)
                    self.lines[row][col] = "."
                elif self.lines[row][col] == "#":
                    for r, stone in enumerate(reversed(picked_up)):
                        stone.c1 = col + r + 1
                        self.lines[row][col + r + 1] = stone
                        self.moving.add((row, col + r + 1))
                    picked_up.clear()
            for r, stone in enumerate(reversed(picked_up)):
                stone.c1 = r
                self.lines[row][r] = stone
                self.moving.add((row, r))
        return self

    def gist(self):
        string = "\n".join(
            "".join(char if isinstance(char, str) else "O" for char in line)
            for line in self.lines
        )
        surface = pg.Surface((self.C, self.R))
        surface.fill(BACKGROUND)
        for r, line in enumerate(self.lines):
            for c, char in enumerate(line):
                if isinstance(char, RollingStone):
                    surface.set_at((c, r), TEXT_COLOR)
        return string, surface

    def mark_stone(self, x, y):
        c = round(x / self.unit - 1.5)
        r = round(y / self.unit - 1.5)
        if c < 0 or c < 0 or c >= self.C or r >= self.C:
            return
        maybe_stone = self.lines[r][c]
        if type(maybe_stone) is RollingStone:
            maybe_stone.marked = not maybe_stone.marked
            self.render()

    def get_gist_img(self, cycle_number):
        if self.period_start > 0 and cycle_number >= self.period_start:
            index = (
                self.period_start - 1 + (cycle_number - self.period_start) % self.period
            )
            return self.gist_imgs[index]
        else:
            return self.gist_imgs[cycle_number - 1]

    def render(self):
        self.surface.blit(self.background, self.background.get_rect())
        self.load = 0
        for r, line in enumerate(self.lines):
            for c, stone in enumerate(line):
                if not isinstance(stone, RollingStone):
                    continue
                x = self.unit * (stone.c + 1.5)
                y = self.unit * (stone.r + 1.5)
                color = WHITE if stone.is_moving else TEXT_COLOR
                if stone.marked:
                    color = RED
                radius = self.unit // 2
                if r <= self.load_row:
                    self.load += self.R - r
                    color = self.load_color
                if r == self.load_row:
                    radius += 1
                pg.draw.circle(self.surface, color, (x, y), radius)

    def do_next_thing(self):
        if self.cycle_number == 1 and self.direction == "N" and self.state == "paused":
            self.calc_load(color=SILVER)
        elif (
            self.period_start > 0
            and (self.cycle_number - self.period_start) % self.period
            == (1_000_000_000 - self.period_start) % self.period
            and self.direction == "E"
            and self.state == "paused"
            and not self.gold_done
        ):
            self.calc_load(color=GOLD)
        elif self.period_start > 0 and self.state == "load":
            self.state = "paused"
            self.pause_left = 2
            self.gold_done = True
        elif self.direction == "E" and self.state == "paused" and self.period < 0:
            string, surface = self.gist()
            if string in self.last_seen_after:
                if self.period_start == -1:
                    self.period_start = self.last_seen_after[string]
                    self.period = self.cycle_number - self.period_start
            elif self.cycle_number > 0:
                self.last_seen_after[string] = self.cycle_number
                self.gist_imgs.append(surface)
            self.state = "x"
            self.do_next_thing()
        else:
            self.direction, tilt = next(self.spin_cycle)
            if self.direction == "N":
                self.cycle_number += 1
            tilt()
            self.state = "tilt"


def run():
    text_input = example_input
    text_input = get_data(year=2023, day=14)
    platform = TiltPlatformVis(text_input, WIDTH, HEIGHT)
    platform.render()

    WP = (WIDTH - platform.surface.get_rect().width) / 2
    HP = (HEIGHT - platform.surface.get_rect().height) / 2
    platform_rect = platform.surface.get_rect(top=HP, left=WP)
    pg.init()
    screen = pg.display.set_mode([WIDTH, HEIGHT])
    pg.display.set_caption("Advent of Code 2023 - Day 14 - Parabolic Reflector Dish")
    font = pg.font.SysFont("monospace", FONT_SIZE)
    totals_font = pg.font.SysFont("monospace", TOTAL_FONT_SIZE)

    clock = pg.time.Clock()

    t0 = time.perf_counter()
    t = 0
    last_t = 0
    paused = False

    running = True
    directions = "NWSE"

    total1 = 0
    total2 = 0

    # main loop
    while running:
        clock.tick(FPS)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                x, y = event.pos
                if (x > 20 and x < 120) and (y > 20 and y < 100):
                    paused = not paused
                platform.mark_stone(x - WP, y - HP)

        t = max(0, time.perf_counter() - t0 - INITIAL_DELAY)
        dt = t - last_t
        last_t = t

        if dt > 0:
            if not paused or platform.state == "tilt":
                platform.update(dt)

        if platform.state == "load":
            if platform.load_color == SILVER:
                total1 = platform.load
            elif platform.load_color == GOLD:
                total2 = platform.load

        if platform.cycle_number > 3:
            if platform.period == -1:
                platform.PAUSE_BETWEEN_ROLLS = 0
                platform.gravity += 300 * dt
            else:
                platform.gravity = 200
                platform.PAUSE_BETWEEN_ROLLS = 0.1

        # erase everything
        screen.fill(BACKGROUND)

        screen.blit(platform.surface, platform_rect)

        # draw cycle number and direction
        cycle_text = font.render(
            "Cycle:" + str(platform.cycle_number).rjust(4) + " ", 1, TEXT_COLOR
        )
        cycle_rect = cycle_text.get_rect(left=WIDTH - WP + 40, top=40)
        screen.blit(cycle_text, cycle_rect)
        rect = cycle_rect
        for direc in directions:
            if direc == platform.direction:
                color = BACKGROUND
                back = TEXT_COLOR
            else:
                color = TEXT_COLOR
                back = None
            dir_text = font.render(direc, 1, color, back)
            dir_rect = dir_text.get_rect(left=rect.right + 5, top=rect.top)
            screen.blit(dir_text, dir_rect)
            rect = dir_rect

        # draw totals
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

        # draw gists
        top = cycle_rect.bottom + 40
        start = platform.cycle_number - 1
        if platform.period > 0 and platform.load > 0:
            start = platform.cycle_number
        for i in range(start, platform.cycle_number - 10, -1):
            if i < 1:
                break
            gist_img = platform.get_gist_img(i)
            gist_rect = gist_img.get_rect(top=top, centerx=WIDTH - WP // 2)
            screen.blit(gist_img, gist_rect)
            top = gist_rect.bottom + 5
            gist_index = font.render(str(i), 1, TEXT_COLOR)
            screen.blit(
                gist_index,
                gist_index.get_rect(
                    centery=gist_rect.centery, right=gist_rect.left - 5
                ),
            )
            if platform.period > 0 and i >= platform.period_start + platform.period:
                same_as = (
                    platform.period_start
                    + (i - platform.period_start) % platform.period
                )
                same_as = font.render(f"=={same_as}", 1, TEXT_COLOR)
                same_as_rect = same_as.get_rect(
                    centery=gist_rect.centery, left=gist_rect.right + 5
                )
                screen.blit(same_as, same_as_rect)
                if (i - platform.period_start) % platform.period == (
                    1_000_000_000 - platform.period_start
                ) % platform.period:
                    same_as_final = font.render("==1e9", 1, GOLD)
                    screen.blit(
                        same_as_final,
                        same_as_final.get_rect(
                            top=same_as_rect.bottom, left=same_as_rect.left
                        ),
                    )

            if top > HEIGHT:
                break

        # # draw pause button
        # pg.draw.rect(screen, TEXT_COLOR, pg.Rect(20, 20, 50, 50))
        # if paused:
        #     pg.draw.lines(
        #         screen, BACKGROUND, True, [(34, 30), (34 + 26, 45), (34, 60)], 4
        #     )
        # else:
        #     pg.draw.line(screen, BACKGROUND, (38, 30), (38, 60), 4)
        #     pg.draw.line(screen, BACKGROUND, (52, 30), (52, 60), 4)
        # actually update the screen now
        pg.display.flip()

    pg.quit()
    sys.exit()


if __name__ == "__main__":
    run()
