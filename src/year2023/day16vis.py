# Problem statement: https://adventofcode.com/2023/day/16

import sys
import time
from random import randint
from math import floor, ceil, sin, sqrt, pi
from aocd import get_data
import pygame as pg
from year2023.day16 import example_input, direction_transforms, MirrorsCave
from util.inputs import movechars_dr_dc

SILVER = (153, 153, 204)
GOLD = (230, 230, 94)
TRANSPARENT = (0, 0, 0, 0)
TEXT_COLOR = (204, 204, 204, 255)
RED = (255, 120, 120)
WHITE = (255, 255, 255, 255)
GRID_COLOR = (100, 100, 100)
BACKGROUND = (15, 15, 35, 255)
BACKGROUND_2 = (25, 25, 55, 255)
LAVA = (207, 16, 32, 255)

WIDTH = 1280
HEIGHT = 720
W_PADDING = 50

FPS = 60
INITIAL_DELAY = 0.5

FONT_SIZE = 20
EPS = 0.001
LIGHT_SOURCE_HEIGHT = 30
LIGHT_SOURCE_WIDTH = round(LIGHT_SOURCE_HEIGHT * sqrt(3) / 2)


def color_noise(n, amount=0.1):
    dn = randint(floor(-n * amount), ceil(n * amount))
    return min(255, max(0, n + dn))


class MirrorsCavern:
    def __init__(self, text, maxwidth, maxheight):
        self.calc_cave = MirrorsCave(text)
        self.lines = text.split("\n")
        # size up and prepare background
        self.maxwidth = maxwidth
        self.maxheight = maxheight
        self.R = len(self.lines)
        self.C = len(self.lines[0])
        self.unit = int(min(maxwidth / (self.C + 2), maxheight / (self.R + 2)))
        self.speed_of_light = 10
        self.surface = pg.Surface(((self.C + 2) * self.unit, (self.R + 2) * self.unit))
        # background surface has borders square
        self.background = self.surface.copy()
        self.background.fill(BACKGROUND)
        pg.draw.rect(
            self.background,
            GRID_COLOR,
            pg.Rect(0, 0, (self.C + 2) * self.unit, (self.R + 2) * self.unit),
            self.unit,
        )
        self.line_width = max(2, self.unit // 4)
        # mirrors surface holds mirrors and splitters
        mirrors_line_width = self.line_width + 2
        self.mirrors = self.surface.convert_alpha()
        self.mirrors.fill(TRANSPARENT)
        for r, line in enumerate(self.lines):
            for c, char in enumerate(line):
                if char == ".":
                    continue
                x0, x1 = self.unit * (c + 1), self.unit * (c + 2)
                y0, y1 = self.unit * (r + 1), self.unit * (r + 2)
                if char == "/":
                    pg.draw.line(
                        self.mirrors,
                        TEXT_COLOR,
                        (x0, y1),
                        (x1, y0),
                        mirrors_line_width,
                    )
                elif char == "\\":
                    pg.draw.line(
                        self.mirrors,
                        TEXT_COLOR,
                        (x0, y0),
                        (x1, y1),
                        mirrors_line_width,
                    )
                elif char == "-":
                    pg.draw.line(
                        self.mirrors,
                        TEXT_COLOR,
                        (x0, (y0 + y1) / 2),
                        (x1, (y0 + y1) / 2),
                        mirrors_line_width,
                    )
                elif char == "|":
                    pg.draw.line(
                        self.mirrors,
                        TEXT_COLOR,
                        ((x0 + x1) / 2, y0),
                        ((x0 + x1) / 2, y1),
                        mirrors_line_width,
                    )
        # lava surface is self explaining...
        self.lava = self.surface.convert_alpha()
        self.lava.fill(TRANSPARENT)

        self.temp = self.surface.copy()
        # beam surface - used for rendering light beams
        self.beam_surface = self.surface.convert_alpha()
        self.beam_surface.fill(TRANSPARENT)
        self.energized = set()
        self.lava_colors = {}
        self.rect = self.surface.get_rect()
        self.origins = list(self.calc_cave.iter_origins())
        self.origin_results = []
        self.best_origin_index = -1
        self.best_energized = 0
        self.total_distance = 0
        self.beams = []
        self.processed = set()
        self.traveling = set()
        self.lightup_time = -1
        self.total_distance = 0
        self.do_lava = False
        self.origin_index = 0

    def decay_color(self, color, distance):
        size_ago = 2 * (self.total_distance - distance) / (self.R + self.C)
        brightness = 1.2 - size_ago
        brightness = min(max(brightness, 0.4), 1)
        color = tuple((*(int(brightness * c) for c in color[:3]), *color[3:]))
        return color

    def update(self, dt):
        # trace the traveling beams
        distance = dt * self.speed_of_light
        self.total_distance += distance
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
                    self.beams.append(((r0, c0), (r, c), self.total_distance))
                    turned = True
                    break
                self.energized.add((r, c))
                newchar = self.lines[r][c]
                if newchar == ".":
                    continue
                newdirs = direction_transforms[newchar][direction]
                turned = True
                for newdir in newdirs:
                    # this beam just turned - add a line before, put leftover beams into traveling
                    self.beams.append(
                        ((r0, c0), (r, c), self.total_distance - distance)
                    )
                    if (r, c, newdir) not in self.processed:
                        self.traveling.add((r, c, newdir, distance))
                break
            # leftover distance is not enough to reach the next mirror
            # add this to traveling
            if not turned:
                traveling.add((r0, c0, direction, distance0))
        self.traveling = traveling
        # print(self.beams, self.traveling)

        # update display
        self.surface.blit(self.background, self.rect)
        if self.lightup_time == -1:
            self.beam_surface.fill(TRANSPARENT)
            for beam in self.beams:
                (r0, c0), (r1, c1), distance_before = beam
                x0, x1 = self.unit * (c0 + 1.5), self.unit * (c1 + 1.5)
                y0, y1 = self.unit * (r0 + 1.5), self.unit * (r1 + 1.5)
                color = self.decay_color(GOLD, distance_before)
                pg.draw.line(
                    self.beam_surface, color, (x0, y0), (x1, y1), self.line_width
                )
                color = self.decay_color(WHITE, distance_before)
                pg.draw.line(
                    self.beam_surface,
                    color,
                    (x0, y0),
                    (x1, y1),
                    max(1, self.line_width // 2),
                )
            for beam in self.traveling:
                r0, c0, direction, distance = beam
                dr, dc = movechars_dr_dc[direction]
                r1, c1 = r0 + dr * distance, c0 + dc * distance
                x0, x1 = self.unit * (c0 + 1.5), self.unit * (c1 + 1.5)
                y0, y1 = self.unit * (r0 + 1.5), self.unit * (r1 + 1.5)
                pg.draw.line(
                    self.beam_surface, GOLD, (x0, y0), (x1, y1), self.line_width
                )
                pg.draw.line(
                    self.beam_surface,
                    WHITE,
                    (x0, y0),
                    (x1, y1),
                    max(1, self.line_width // 2),
                )
            pg.draw.rect(
                self.beam_surface,
                TRANSPARENT,
                pg.Rect(0, 0, (self.C + 2) * self.unit, (self.R + 2) * self.unit),
                self.unit,
            )
            self.surface.blit(self.beam_surface, self.rect)

            if len(self.traveling) == 0:
                self.origin_results[self.origin_index] = len(self.energized)
                if len(self.energized) > self.best_energized:
                    self.best_energized = len(self.energized)
                    self.best_origin_index = self.origin_index
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
        else:
            self.lightup_time += dt
            if self.do_lava:
                self.lava.fill(TRANSPARENT)
                for r, c in self.energized:
                    if (
                        r < 0
                        or r >= len(self.lines)
                        or c < 0
                        or c >= len(self.lines[0])
                    ):
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
                            self.unit * (c + 1),
                            self.unit * (r + 1),
                            self.unit,
                            self.unit,
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
            else:
                self.surface.blit(self.beam_surface, self.rect)

        self.surface.blit(self.mirrors, self.rect)

    def light_up(self, origin_index, do_lava=True):
        self.origin_index = origin_index
        self.beams = []
        self.processed = set()
        self.traveling = set((tuple([*self.origins[origin_index], 0]),))
        self.lightup_time = -1
        self.lava_colors.clear()
        self.total_distance = 0
        self.do_lava = do_lava
        self.energized = set()

    def get_light_source_position(self, light_source, origin_index=None):
        if origin_index is None:
            origin_index = self.origin_index
        r, c, direction = self.origins[origin_index]
        if direction == ">":
            rotated = light_source
            rect = rotated.get_rect(
                right=self.unit * (c + 2), centery=self.unit * (r + 1.5)
            )
        elif direction == "<":
            rotated = pg.transform.rotate(light_source, 180)
            rect = rotated.get_rect(
                left=self.unit * (c + 1), centery=self.unit * (r + 1.5)
            )
        elif direction == "^":
            rotated = pg.transform.rotate(light_source, 90)
            rect = rotated.get_rect(
                centerx=self.unit * (c + 1.5), top=self.unit * (r + 1)
            )
        elif direction == "v":
            rotated = pg.transform.rotate(light_source, -90)
            rect = rotated.get_rect(
                centerx=self.unit * (c + 1.5), bottom=self.unit * (r + 2)
            )
        return rotated, rect

    def calc_another_origin(self):
        if len(self.origin_results) < len(self.origins):
            origin = self.origins[len(self.origin_results)]
            cnt = self.calc_cave.count_energized_tiles(origin)
            self.origin_results.append(cnt)
            if cnt > self.best_energized:
                self.best_energized = cnt
                self.best_origin_index = len(self.origin_results) - 1


def run():
    pg.init()
    screen = pg.display.set_mode([WIDTH, HEIGHT])
    pg.display.set_caption("Advent of Code 2023 - Day 16 - The Floor Will Be Lava")

    text_input = example_input
    text_input = get_data(year=2023, day=16)
    cave = MirrorsCavern(text_input, WIDTH, HEIGHT)

    WP = (WIDTH - cave.surface.get_rect().width) / 2
    HP = (HEIGHT - cave.surface.get_rect().height) / 2
    cave_rect = cave.surface.get_rect(top=HP, left=WP)
    font = pg.font.SysFont("monospace", FONT_SIZE)

    clock = pg.time.Clock()
    # prepare light source
    light_sources = {}
    for color in (WHITE, SILVER, GOLD):
        light_source = pg.Surface(
            (LIGHT_SOURCE_WIDTH, LIGHT_SOURCE_HEIGHT)
        ).convert_alpha()
        light_source.fill(TRANSPARENT)
        pg.draw.polygon(
            light_source,
            color,
            [
                (0, 0),
                (LIGHT_SOURCE_WIDTH, LIGHT_SOURCE_HEIGHT / 2),
                (0, LIGHT_SOURCE_HEIGHT),
                (LIGHT_SOURCE_WIDTH // 4, LIGHT_SOURCE_HEIGHT / 2),
            ],
        )
        light_sources[color] = light_source

    t0 = time.perf_counter()
    t = 0
    last_t = 0
    light_finished_at = -1
    origin_index = -1

    part1_total = 0
    part2_total = 0
    current_total = 0

    running = True

    cave.speed_of_light = 0.2 * (cave.R + cave.C)
    # main loop
    while running:
        clock.tick(FPS)

        cave.calc_another_origin()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                pass

        t = max(0, time.perf_counter() - t0 - INITIAL_DELAY)
        dt = t - last_t
        last_t = t

        if len(cave.traveling) == 0 and light_finished_at == -1:
            if part1_total == 0:
                part1_total = len(cave.energized)
            if part2_total < len(cave.energized):
                part2_total = len(cave.energized)
            light_finished_at = t
            if part1_total == 0:
                origin_index = 0
            elif cave.do_lava:
                light_finished_at = -1
            else:
                origin_index = next(
                    (
                        i
                        for i, cnt in enumerate(cave.origin_results)
                        if cnt > part2_total
                    ),
                    origin_index,
                )
                # origin_index = (origin_index + 120) % len(cave.origins)
        if light_finished_at != -1 and t - light_finished_at > 2:
            cave.light_up(origin_index, do_lava=origin_index == cave.best_origin_index)
            light_finished_at = -1
            current_total = 0

        # erase everything
        screen.fill(BACKGROUND)

        # draw platform
        cave.update(dt)
        current_total = len(cave.energized)

        screen.blit(cave.surface, cave_rect)

        if part1_total > 0:
            # render part 1 light source and total
            rotated_light_source, rect = cave.get_light_source_position(
                light_sources[SILVER], origin_index=0
            )
            rect.top += HP
            rect.left += WP
            screen.blit(rotated_light_source, rect)
            total1 = font.render(
                f"Part 1: {part1_total}",
                1,
                SILVER,
            )
            if rect.centerx < WIDTH // 2:
                total1_rect = total1.get_rect(
                    centery=rect.centery, right=rect.left - 10
                )
            else:
                total1_rect = total1.get_rect(
                    centery=rect.centery, left=rect.right + 10
                )
            screen.blit(total1, total1_rect)

        # render part2 light source
        if cave.do_lava and cave.lightup_time >= 0:
            rotated_light_source, rect = cave.get_light_source_position(
                light_sources[GOLD], cave.best_origin_index
            )
            rect.top += HP
            rect.left += WP
            screen.blit(rotated_light_source, rect)
            total2 = font.render(
                f"Part 2: {part2_total}",
                1,
                GOLD,
            )
            if rect.centerx < WIDTH // 2:
                total2_rect = total2.get_rect(
                    centery=rect.centery, right=rect.left - 10
                )
            else:
                total2_rect = total2.get_rect(
                    centery=rect.centery, left=rect.right + 10
                )
            screen.blit(total2, total2_rect)
        else:
            # render current light source
            rotated_light_source, rect = cave.get_light_source_position(
                light_sources[WHITE]
            )
            rect.top += HP
            rect.left += WP
            screen.blit(rotated_light_source, rect)

            total = font.render(str(current_total), 1, WHITE)
            if rect.left <= WIDTH // 2:
                total_rect = total.get_rect(right=rect.left - 10, centery=rect.centery)
            else:
                total_rect = total.get_rect(left=rect.right + 10, centery=rect.centery)
            screen.blit(total, total_rect)

        # actually update the screen now
        pg.display.flip()

    pg.quit()
    sys.exit()


if __name__ == "__main__":
    run()
