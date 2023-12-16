# Problem statement: https://adventofcode.com/2023/day/16

import sys
import time
from random import randint
from math import floor, ceil, sin
from aocd import get_data
import pygame as pg
from year2023.day16 import example_input, direction_transforms
from util.inputs import movechars_dr_dc

SILVER = (153, 153, 204)
GOLD = (230, 230, 94)
TRANSPARENT = (0, 0, 0, 0)
TEXT_COLOR = (204, 204, 204, 255)
RED = (255, 120, 120)
WHITE = (255, 255, 255)
GRID_COLOR = (100, 100, 100)
BACKGROUND = (15, 15, 35, 255)
BACKGROUND_2 = (25, 25, 55, 255)
LAVA = (207, 16, 32, 255)

WIDTH = 1280
HEIGHT = 720
W_PADDING = 50

FPS = 60
INITIAL_DELAY = 2

FONT_SIZE = 20
EPS = 0.001


def color_noise(n, amount=0.1):
    dn = randint(floor(-n * amount), ceil(n * amount))
    return min(255, max(0, n + dn))


class MirrorsCavern:
    def __init__(self, text, maxwidth, maxheight):
        self.lines = text.split("\n")
        # size up and prepare background
        self.maxwidth = maxwidth
        self.maxheight = maxheight
        self.R = len(self.lines)
        self.C = len(self.lines[0])
        self.unit = int(min(maxwidth / (self.C + 2), maxheight / (self.R + 2)))
        self.speed_of_light = 10
        self.surface = pg.Surface(((self.C + 2) * self.unit, (self.R + 2) * self.unit))
        self.background = self.surface.copy()
        self.background.fill(BACKGROUND)
        pg.draw.rect(
            self.background,
            GRID_COLOR,
            pg.Rect(0, 0, (self.C + 2) * self.unit, (self.R + 2) * self.unit),
            self.unit,
        )
        line_width = max(2, self.unit // 4)
        self.mirrors = self.surface.copy()
        self.mirrors.fill((0, 0, 0, 0))
        for r, line in enumerate(self.lines):
            for c, char in enumerate(line):
                if char == ".":
                    continue
                x0, x1 = self.unit * (c + 1), self.unit * (c + 2)
                y0, y1 = self.unit * (r + 1), self.unit * (r + 2)
                if char == "/":
                    pg.draw.line(
                        self.mirrors, TEXT_COLOR, (x0, y1), (x1, y0), line_width
                    )
                elif char == "\\":
                    pg.draw.line(
                        self.mirrors, TEXT_COLOR, (x0, y0), (x1, y1), line_width
                    )
                elif char == "-":
                    pg.draw.line(
                        self.mirrors,
                        TEXT_COLOR,
                        (x0, (y0 + y1) / 2),
                        (x1, (y0 + y1) / 2),
                        line_width,
                    )
                elif char == "|":
                    pg.draw.line(
                        self.mirrors,
                        TEXT_COLOR,
                        ((x0 + x1) / 2, y0),
                        ((x0 + x1) / 2, y1),
                        line_width,
                    )
        self.lava = self.surface.copy()
        self.temp = self.surface.copy()
        self.beam_surface = self.surface.copy()
        self.lava.fill(TRANSPARENT)
        self.energized = set()
        self.lava_colors = {}
        self.rect = self.surface.get_rect()

    def update(self, dt):
        # trace the traveling beams
        distance = dt * self.speed_of_light
        self.traveling = set(
            (r0, c0, direction, leftover_dist + distance)
            for (r0, c0, direction, leftover_dist) in self.traveling
        )
        traveling = set()
        while len(self.traveling) > 0:
            r0, c0, direction, distance0 = self.traveling.pop()
            distance = distance0
            r, c = r0, c0
            dr, dc = movechars_dr_dc[direction]
            self.processed.add((r, c, direction))
            turned = False
            while distance > 1:
                distance -= 1
                r, c = r + dr, c + dc
                if r < 0 or r >= len(self.lines) or c < 0 or c >= len(self.lines[0]):
                    # this beam is finished, won't go anywhere else
                    self.beams.add(((r0, c0), (r, c)))
                    turned = True
                    break
                self.energized.add((r, c))
                newchar = self.lines[r][c]
                newdirs = direction_transforms[newchar][direction]
                if newdirs == direction:
                    continue
                turned = True
                for newdir in newdirs:
                    # this beam just turned - add a line before, put leftover beams into traveling
                    self.beams.add(((r0, c0), (r, c)))
                    if (r, c, newdir) not in self.processed:
                        self.traveling.add((r, c, newdir, distance))
                break
            # leftover distance is not enough to reach the next mirror
            # add this to traveling
            if not turned:
                traveling.add((r0, c0, direction, distance0))
        self.traveling = traveling

        # update display
        self.surface.blit(self.background, self.background.get_rect())
        if len(self.traveling) > 0:
            self.beam_surface.fill(TRANSPARENT)
            for beam in self.beams:
                (r0, c0), (r1, c1) = beam
                x0, x1 = self.unit * (c0 + 1.5), self.unit * (c1 + 1.5)
                y0, y1 = self.unit * (r0 + 1.5), self.unit * (r1 + 1.5)
                pg.draw.line(self.beam_surface, GOLD, (x0, y0), (x1, y1), 4)
            for beam in self.traveling:
                r0, c0, direction, distance = beam
                dr, dc = movechars_dr_dc[direction]
                r1, c1 = r0 + dr * distance, c0 + dc * distance
                x0, x1 = self.unit * (c0 + 1.5), self.unit * (c1 + 1.5)
                y0, y1 = self.unit * (r0 + 1.5), self.unit * (r1 + 1.5)
                pg.draw.line(self.beam_surface, GOLD, (x0, y0), (x1, y1), 4)
            for beam in self.beams:
                (r0, c0), (r1, c1) = beam
                x0, x1 = self.unit * (c0 + 1.5), self.unit * (c1 + 1.5)
                y0, y1 = self.unit * (r0 + 1.5), self.unit * (r1 + 1.5)
                pg.draw.line(self.beam_surface, WHITE, (x0, y0), (x1, y1), 2)
            for beam in self.traveling:
                r0, c0, direction, distance = beam
                dr, dc = movechars_dr_dc[direction]
                r1, c1 = r0 + dr * distance, c0 + dc * distance
                x0, x1 = self.unit * (c0 + 1.5), self.unit * (c1 + 1.5)
                y0, y1 = self.unit * (r0 + 1.5), self.unit * (r1 + 1.5)
                pg.draw.line(self.beam_surface, WHITE, (x0, y0), (x1, y1), 2)
                pg.draw.rect(
                    self.beam_surface,
                    TRANSPARENT,
                    pg.Rect(0, 0, (self.C + 2) * self.unit, (self.R + 2) * self.unit),
                    self.unit,
                )
            self.surface.blit(self.beam_surface, self.rect, None, pg.BLEND_ADD)
        else:
            if self.lightup_time == -1:
                print(len(self.energized))
                self.lightup_time = 0
                self.lava_colors = {}
                red, green, blue, alpha = LAVA
                for pos in self.energized:
                    self.lava_colors[pos] = (
                        color_noise(red),
                        color_noise(green),
                        color_noise(blue),
                        alpha,
                    )
            self.lightup_time += dt
            self.lava.fill(TRANSPARENT)
            for r, c in self.energized:
                if r < 0 or r >= len(self.lines) or c < 0 or c >= len(self.lines[0]):
                    continue
                red, green, blue, alpha = self.lava_colors[r, c]
                deg = max(
                    0,
                    0.8 + 0.2 * sin(self.lightup_time + 0.08 * r),
                )
                color = (
                    int(red * deg),
                    int(green * deg),
                    int(blue * deg),
                    alpha,
                )
                self.lava.fill(
                    color,
                    pg.Rect(
                        self.unit * (c + 1), self.unit * (r + 1), self.unit, self.unit
                    ),
                )
            if self.lightup_time < 3:
                self.temp.blit(self.background, self.rect)
                self.temp.blit(self.beam_surface, self.rect, None, pg.BLEND_ADD)
                self.temp.set_alpha(
                    255 * (1 - min(1, max(0, self.lightup_time - 1.5) / 1.5))
                )
                self.surface.blit(self.temp, self.rect)
            self.temp.blit(self.background, self.rect)
            self.temp.blit(self.lava, self.rect, None, pg.BLEND_ADD)
            self.temp.set_alpha(255 * min(1, self.lightup_time / 3))
            self.surface.blit(self.temp, self.rect)

        self.surface.blit(
            self.mirrors, self.mirrors.get_rect(), None, pg.BLEND_RGBA_ADD
        )

    def light_up(self, origin):
        self.origin = origin
        self.beams = set()
        self.processed = set()
        self.traveling = set((tuple([*origin, 0]),))
        self.lightup_time = -1
        self.lava_colors.clear()


def run():
    text_input = example_input
    text_input = get_data(year=2023, day=16)
    cave = MirrorsCavern(text_input, WIDTH, HEIGHT)
    # print(len(universe.exp_c), len(universe.exp_r))
    cave.speed_of_light = 20
    WP = (WIDTH - cave.surface.get_rect().width) / 2
    HP = (HEIGHT - cave.surface.get_rect().height) / 2
    cave_rect = cave.surface.get_rect(top=HP, left=WP)
    pg.init()
    screen = pg.display.set_mode([WIDTH, HEIGHT])
    pg.display.set_caption("Advent of Code 2023 - Day 16 - The Floor Will Be Lava")
    font = pg.font.SysFont("monospace", FONT_SIZE)

    clock = pg.time.Clock()

    t0 = time.perf_counter()
    t = 0
    last_t = 0

    running = True
    cave.light_up((0, -1, ">"))
    # main loop
    while running:
        clock.tick(FPS)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                pass

        t = max(0, time.perf_counter() - t0 - INITIAL_DELAY)
        dt = t - last_t
        last_t = t

        # erase everything
        screen.fill(BACKGROUND)

        # draw platform
        cave.update(dt)

        screen.blit(cave.surface, cave_rect, None, pg.BLEND_ALPHA_SDL2)

        # actually update the screen now
        pg.display.flip()

    pg.quit()
    sys.exit()


if __name__ == "__main__":
    run()
