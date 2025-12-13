# Problem statement: https://adventofcode.com/2023/day/21

import sys
from collections import Counter
import time
from random import randint
from math import floor, ceil, sin, sqrt
from aocd import get_data
import pygame as pg
from year2023.day21 import example_input, FarmWorld
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

FPS = 5
INITIAL_DELAY = 2

FONT_SIZE = 20
EPS = 0.001
LIGHT_SOURCE_HEIGHT = 30
LIGHT_SOURCE_WIDTH = round(LIGHT_SOURCE_HEIGHT * sqrt(3) / 2)


def run():
    pg.init()
    screen = pg.display.set_mode([WIDTH, HEIGHT])
    pg.display.set_caption("Advent of Code 2023 - Day 21 - Step Counter")

    text_input = example_input
    # text_input = get_data(year=2023, day=21)
    lines = text_input.split("\n")
    start_pos = None
    for r, line in enumerate(lines):
        for c, char in enumerate(line):
            if char == "S":
                start_pos = (r, c)
                lines[r] = line.replace("S", ".")
                break
        if start_pos is not None:
            break
    for r, line in enumerate(lines):
        lines[r] = line[:-1]
    queue = set((start_pos,))
    R = len(lines)
    C = len(lines[0])
    initial_rhombus = R // 2
    rs, cs = start_pos
    # world = FarmWorld(text_input)
    print(R, C)
    font = pg.font.SysFont("monospace", FONT_SIZE)

    clock = pg.time.Clock()

    t0 = time.perf_counter()
    t = 0
    last_t = 0
    running = True
    paused = False
    steps = 0
    rhomb_counts = {}
    # main loop
    while running:
        clock.tick(FPS)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                paused = not paused

        t = max(8, time.perf_counter() - t0 - INITIAL_DELAY)
        dt = t - last_t
        last_t = t
        if paused:
            continue
        RANGE = 400
        unit = max(4, min(WIDTH // RANGE, HEIGHT // RANGE))

        def x(c):
            return WIDTH // 2 + unit * (c - start_pos[1])

        def y(r):
            return HEIGHT // 2 + unit * (r - start_pos[0])

        if t > 0:
            # world.take_step()
            steps += 1
            new_queue = set()
            while len(queue) > 0:
                r0, c0 = queue.pop()
                for direction in "<>^v":
                    dr, dc = movechars_dr_dc[direction]
                    r, c = r0 + dr, c0 + dc
                    ri = (r + R) % R
                    ci = (c + C) % C
                    if lines[ri][ci] == "#":
                        continue
                    new_queue.add((r, c))
            queue = new_queue
            if steps % R == initial_rhombus:
                print(steps, len(queue))
                rhomb_counts = Counter()
                for r, c in queue:
                    ri, ci = r - rs, c - cs
                    k, t = ci - ri, ci + ri
                    K, T = round(k / R), round(t / R)
                    rhomb_counts[(K, T)] += 1
                paused = True
            # if world.total != len(queue):
            #     paused = True
        if steps % 1 == 0:
            screen.fill(BACKGROUND)
            for r in range(start_pos[0] - RANGE // 2, start_pos[0] + RANGE // 2):
                for c in range(start_pos[1] - RANGE // 2, start_pos[1] + RANGE // 2):
                    ri = (r + 100 * R) % R
                    ci = (c + 100 * C) % C
                    if lines[ri][ci] == "#":
                        pg.draw.rect(
                            screen,
                            GRID_COLOR,
                            pg.Rect(x(c) - unit / 2, y(r) - unit / 2, unit, unit),
                        )
                    if (r, c) in queue:
                        pg.draw.circle(screen, TEXT_COLOR, (x(c), y(r) + 1), unit / 2)
            if paused:
                for (K, T), cnt in rhomb_counts.items():
                    c = cs + C * (K + T) / 2
                    r = rs + R * (T - K) / 2
                    text = font.render(str(cnt), 1, TEXT_COLOR, BACKGROUND)
                    rect = text.get_rect(centerx=x(c), centery=y(r))
                    screen.blit(text, rect)
                print(Counter(rhomb_counts.values()).most_common())
            # for tile in world.tiles.values():
            #     if tile.is_repeating:
            #         continue
            #     for r, c in tile.queue:
            #         pg.draw.circle(
            #             screen, RED, (x(c + tile.pc * C), y(r + tile.pr * R)), unit / 2
            #         )
            text = font.render(f"Steps: {steps}", 1, TEXT_COLOR, BACKGROUND)
            rect = text.get_rect(top=10, left=10)
            screen.blit(text, rect)
            text = font.render(f"Total 1: {len(queue)}", 1, TEXT_COLOR, BACKGROUND)
            rect = text.get_rect(top=rect.bottom, left=10)
            screen.blit(text, rect)
            # text = font.render(f"Total 2: {world.total}", 1, TEXT_COLOR, BACKGROUND)
            # rect = text.get_rect(top=rect.bottom, left=10)
            # screen.blit(text, rect)
            # actually update the screen now
            pg.display.flip()

    pg.quit()
    sys.exit()


if __name__ == "__main__":
    run()
