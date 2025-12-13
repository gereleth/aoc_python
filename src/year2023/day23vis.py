# Problem statement: https://adventofcode.com/2023/day/23

import sys
from collections import Counter
import time
from random import randint
from math import floor, ceil, sin, sqrt
from aocd import get_data
import pygame as pg
from year2023.day23 import example_input, HikingArea
from util.inputs import movechars_dr_dc
# from networkx import Graph

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


class HikingAreaVis:
    def __init__(self, text_input, screen):
        self.area1 = HikingArea(text_input, slippery=True)
        self.area2 = HikingArea(text_input, slippery=False)
        self.R = self.area1.R
        self.C = self.area1.C
        self.screen = screen
        self.rect = screen.get_rect()
        self.background = screen.copy()
        self.state = "initial"
        self.t = 0
        self.unit, self.c_to_x, self.r_to_y = self.size_up()
        self.draw_background()

    def size_up(self):
        RANGE = max(self.R + 1, self.C + 1)
        unit = max(4, min(WIDTH // RANGE, HEIGHT // RANGE))

        def c_to_x(c):
            return WIDTH // 2 + unit * (c - self.C // 2)

        def r_to_y(r):
            return HEIGHT // 2 + unit * (r - self.R // 2)

        return unit, c_to_x, r_to_y

    def draw_background(self):
        u = self.unit // 2
        self.background.fill(BACKGROUND)
        triangles = []
        for r in range(self.R):
            for c in range(self.C):
                char = self.area1.map[r][c]
                x = self.c_to_x(c)
                y = self.r_to_y(r)
                if char == "#":
                    pg.draw.rect(
                        self.background,
                        GRID_COLOR,
                        pg.Rect(
                            x - self.unit / 2,
                            y - self.unit / 2,
                            self.unit,
                            self.unit,
                        ),
                    )
                elif self.area1.map[r][c] == ">":
                    triangles.append(
                        [
                            (x + u, y),
                            (x - u, y + u),
                            (x - u, y - u),
                        ]
                    )
                elif self.area1.map[r][c] == "<":
                    triangles.append(
                        [
                            (x - u, y),
                            (x + u, y + u),
                            (x + u, y - u),
                        ]
                    )
                elif self.area1.map[r][c] == "v":
                    triangles.append(
                        [
                            (x, y + u),
                            (x - u, y - u),
                            (x + u, y - u),
                        ]
                    )
                elif self.area1.map[r][c] == "^":
                    triangles.append(
                        [
                            (x, y - u),
                            (x - u, y + u),
                            (x + u, y + u),
                        ]
                    )
        for triangle in triangles:
            pg.draw.polygon(self.background, WHITE, triangle)

    def update(self, dt):
        self.t += dt
        if self.state == "initial":
            pass

    def next_state(self):
        if self.state == "initial":
            if self.t >= INITIAL_DELAY:
                self.state = "walk"

    def render(self):
        if self.state == "initial":
            self.screen.blit(self.background, self.rect)


def run():
    pg.init()
    screen = pg.display.set_mode([WIDTH, HEIGHT])
    pg.display.set_caption("Advent of Code 2023 - Day 21 - Step Counter")

    text_input = example_input
    text_input = get_data(year=2023, day=23)
    font = pg.font.SysFont("monospace", FONT_SIZE)

    vis = HikingAreaVis(text_input, screen)

    clock = pg.time.Clock()

    t0 = time.perf_counter()
    t = 0
    last_t = 0
    running = True
    paused = False

    small_font = pg.font.SysFont("monospace", max(12, vis.unit))

    # def path_to_lines(path):
    #     points = []
    #     for node in path:
    #         r, c = area1.graph.nodes[node]["position"]
    #         points.append((x(c), y(r)))
    #     return points

    # def path_to_tiles(path):
    #     r, c = rs, cs
    #     points = set([(r, c)])
    #     for char in path:
    #         dr, dc = movechars_dr_dc[char]
    #         r += dr
    #         c += dc
    #         points.add((r, c))
    #     return points

    # main loop
    while running:
        clock.tick(FPS)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                paused = not paused

        t = max(0, time.perf_counter() - t0 - INITIAL_DELAY)
        dt = t - last_t
        last_t = t
        if paused:
            continue

        vis.update(dt)
        vis.render()

        # for n1, n2 in area1.graph.out_edges:
        #     r1, c1 = area1.graph.nodes[n1]["position"]
        #     r2, c2 = area1.graph.nodes[n2]["position"]
        #     x1, y1, x2, y2 = x(c1), y(r1), x(c2), y(r2)
        #     dx, dy = x2 - x1, y2 - y1
        #     dist = sqrt(dx**2 + dy**2)
        #     pg.draw.line(screen, TEXT_COLOR, (x1, y1), (x2, y2), 2)
        #     if area1.slippery:
        #         pg.draw.line(
        #             screen,
        #             TEXT_COLOR,
        #             (x2 - dx * 30 / dist, y2 - dy * 30 / dist),
        #             (x2 - dx * 10 / dist, y2 - dy * 10 / dist),
        #             9,
        #         )
        #     cost = area1.graph.edges[n1, n2]["cost"]
        #     text = small_font.render(str(cost), 1, TEXT_COLOR, BACKGROUND)
        #     rect = text.get_rect(centerx=(x1 + x2) / 2, centery=(y1 + y2) / 2)
        #     screen.blit(text, rect)

        # for node, data in area1.graph.nodes.items():
        #     r, c = data["position"]
        #     coord = (x(c), y(r))
        #     # pg.draw.circle(screen, TEXT_COLOR, coord, unit)
        #     text = small_font.render(str(node), 1, BACKGROUND, TEXT_COLOR)
        #     rect = text.get_rect(center=coord)
        #     screen.blit(text, rect)

        # text = font.render(f"Best path: {bestlen}", 1, TEXT_COLOR, BACKGROUND)
        # rect = text.get_rect(top=10, left=10)
        # screen.blit(text, rect)
        # text = font.render(f"Queue: {queuelen}", 1, TEXT_COLOR, BACKGROUND)
        # rect = text.get_rect(top=rect.bottom, left=10)
        # screen.blit(text, rect)
        # text = font.render(f"Priority: {priority}", 1, TEXT_COLOR, BACKGROUND)
        # rect = text.get_rect(top=rect.bottom, left=10)
        # screen.blit(text, rect)

        pg.display.flip()

    pg.quit()
    sys.exit()


if __name__ == "__main__":
    run()
