# Problem statement: https://adventofcode.com/2023/day/6

import sys
import numpy as np
import time
from aocd import get_data
import pygame as pg
from math import pi, sin, cos, floor
from year2023.day06 import ways_to_win

SILVER = (153, 153, 204)
GOLD = (230, 230, 94)
TEXT_COLOR = (204, 204, 204)
BACKGROUND = (15, 15, 35, 255)
BACKGROUND_2 = (25, 25, 55)

WIDTH = 1280
HEIGHT = 720
W_PADDING = 50
TOTALS_HEIGHT = 60

FPS = 60
INITIAL_DELAY = 2
BOAT_RACE_TIME = 7
BOAT_SIZE = 10


def annotate(text_input):
    time, distance = text_input.split("\n")
    time = time.split(":")[1].strip().split()
    distance = distance.split(":")[1].strip().split()
    silvers = [(int(t), int(d)) for t, d in zip(time, distance)]
    gold = int("".join(time)), int("".join(distance))
    races = [BoatRace(*race) for race in (silvers + [gold])]
    return races


def draw_boat(color, charge_pct):
    surf = pg.Surface((2 * BOAT_SIZE, 2 * BOAT_SIZE))
    surf.fill((0, 0, 0, 0))
    pg.draw.circle(surf, color, (BOAT_SIZE, BOAT_SIZE), BOAT_SIZE, 0)
    if charge_pct > 0.99:
        return surf
    # erase part of filled circle by drawing a polygon on top
    angle = pi / 2 - 2 * pi * charge_pct
    points = [
        (BOAT_SIZE, BOAT_SIZE),
        (
            BOAT_SIZE + 2 * BOAT_SIZE * cos(angle),
            BOAT_SIZE - 2 * BOAT_SIZE * sin(angle),
        ),
    ]
    if angle > -pi / 2:
        points += [(2 * BOAT_SIZE, 2 * BOAT_SIZE)]
    if angle > -pi:
        points += [(0, 2 * BOAT_SIZE)]
    points += [(0, 0), (BOAT_SIZE, 0)]
    pg.draw.polygon(surf, (0, 0, 0, 0), points)
    # bring back circle border
    pg.draw.circle(surf, color, (BOAT_SIZE, BOAT_SIZE), BOAT_SIZE, 2)
    return surf


class BoatRace:
    def __init__(self, time, distance):
        self.time = time
        self.distance = distance
        if time < 100:
            self.boat_charge = np.zeros((time + 1,))
            self.boat_pos = np.zeros_like(self.boat_charge)
            self.boat_idx = np.arange(len(self.boat_charge))
        else:
            self.boat_idx = np.linspace(0, time, 200)
            self.boat_pos = self.boat_idx * (time - self.boat_idx)
        self.xmin = -1
        self.xmax = time + 1
        self.ymin = -1
        self.ymax = int(time**2 / 4) + 1
        self.ways_to_win = ways_to_win(self.time, self.distance)

    def update(self, share_done):
        t = self.time * share_done
        self.boat_charge = np.minimum(self.boat_idx, t)
        self.boat_pos = np.maximum(0, self.boat_charge * (t - self.boat_idx))

    def x_pixels(self, x):
        return W_PADDING + (x - self.xmin) / (self.xmax - self.xmin) * (
            WIDTH - 2 * W_PADDING
        )

    def y_pixels(self, y):
        return (
            HEIGHT
            - W_PADDING
            - (y - self.ymin) / (self.ymax - self.ymin) * (HEIGHT - 2 * W_PADDING)
        )


def run():
    # Get sizes from input data
    text_input = get_data(year=2023, day=6)
    races = annotate(text_input)

    pg.init()
    screen = pg.display.set_mode([WIDTH, HEIGHT])
    pg.display.set_caption("Advent of Code 2023 - Day 6 - Wait For It")

    font = pg.font.SysFont("monospace", 20)
    clock = pg.time.Clock()

    t0 = time.perf_counter()
    running = True

    part_1_total_label = font.render("Part 1: ", 1, SILVER)
    part_1_total_label_rect = part_1_total_label.get_rect(
        centery=TOTALS_HEIGHT // 2, right=WIDTH // 4
    )

    part_2_total_label = font.render("Part 2: ", 1, GOLD)
    part_2_total_label_rect = part_1_total_label.get_rect(
        centery=TOTALS_HEIGHT // 2, right=WIDTH * 3 // 4
    )
    # main loop
    while running:
        clock.tick(FPS)

        t = max(0, time.perf_counter() - t0 - INITIAL_DELAY)
        turn = min(floor(t / BOAT_RACE_TIME), len(races) - 1)
        dt = max(0, min(1, (t - turn * BOAT_RACE_TIME) / BOAT_RACE_TIME))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                t0 = time.perf_counter()

        # erase everything
        screen.fill(BACKGROUND)

        # draw totals
        screen.blit(part_1_total_label, part_1_total_label_rect)
        screen.blit(part_2_total_label, part_2_total_label_rect)
        if turn > 0:
            total = 1
            for race in races[: min(turn, len(races) - 1)]:
                total *= race.ways_to_win
            part_1_total_value = font.render(str(total), 1, SILVER)
            part_1_total_value_rect = part_1_total_value.get_rect(
                centery=TOTALS_HEIGHT // 2, left=WIDTH // 4
            )
            screen.blit(part_1_total_value, part_1_total_value_rect)

        if turn < len(races) - 1:
            # part 1 animation - boats charge up and go
            boat_race = races[turn]
            boat_race.update(min(1, dt / 0.8))
            y0 = boat_race.y_pixels(boat_race.distance)
            pg.draw.line(screen, SILVER, (W_PADDING, y0), (WIDTH - W_PADDING, y0), 1)
            current_total = 0
            for i, boat_pos in enumerate(boat_race.boat_pos):
                x = boat_race.x_pixels(i)
                y = boat_race.y_pixels(boat_pos)
                color = TEXT_COLOR if y > y0 else SILVER
                current_total += y < y0
                charge_pct = boat_race.boat_charge[i] / boat_race.time
                boat = draw_boat(color, charge_pct)
                screen.blit(
                    boat, boat.get_rect(centerx=x, centery=y), None, pg.BLEND_MAX
                )
                if y + BOAT_SIZE < y0:
                    pg.draw.line(screen, SILVER, (x, y0), (x, y + BOAT_SIZE), 1)
            # render current total
            text = font.render(str(current_total), 1, SILVER)
            rect = text.get_rect(top=y0, left=boat_race.x_pixels(0))
            screen.blit(text, rect)
        else:
            # part 2 - just draw a parabola
            boat_race = races[-1]
            max_idx = int(min(1, dt / 0.3) * len(boat_race.boat_pos))
            if max_idx < 2:
                continue
            boat_race = races[-1]
            y0 = boat_race.y_pixels(boat_race.distance)
            pg.draw.line(screen, GOLD, (W_PADDING, y0), (WIDTH - W_PADDING, y0), 1)
            pg.draw.lines(
                screen,
                TEXT_COLOR,
                False,
                [
                    (boat_race.x_pixels(px), boat_race.y_pixels(py))
                    for px, py in zip(
                        boat_race.boat_idx[:max_idx], boat_race.boat_pos[:max_idx]
                    )
                ],
                2,
            )
            x0 = boat_race.x_pixels((boat_race.time - boat_race.ways_to_win) / 2)
            x1 = boat_race.x_pixels((boat_race.time + boat_race.ways_to_win) / 2)
            x = boat_race.x_pixels(boat_race.boat_idx[max_idx - 1])
            if x > x0:
                pg.draw.line(
                    screen,
                    GOLD,
                    (x0, y0),
                    (min(x1, x), y0),
                    5,
                )
            if x > x1:
                part_2_total_value = font.render(str(boat_race.ways_to_win), 1, GOLD)
                part_2_total_value_rect = part_1_total_value.get_rect(
                    centery=TOTALS_HEIGHT // 2, left=WIDTH * 3 // 4
                )
                screen.blit(part_2_total_value, part_2_total_value_rect)
        # actually update the screen now
        pg.display.flip()

    pg.quit()
    sys.exit()


if __name__ == "__main__":
    run()
