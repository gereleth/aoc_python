# Problem statement: https://adventofcode.com/2023/day/10

import sys
import time
from aocd import get_data
import pygame as pg
from year2023.day10 import directions, opposite
from util.inputs import movechars_dr_dc

SILVER = (153, 153, 204)
GOLD = (230, 230, 94)
TEXT_COLOR = (204, 204, 204)
GREY_COLOR = (64, 64, 64)
BACKGROUND = (15, 15, 35, 255)
BACKGROUND_2 = (25, 25, 55)

WIDTH = 1280
HEIGHT = 720
W_PADDING = 50

FPS = 60
INITIAL_DELAY = 2
FONT_SIZE = 20


class PipeMaze:
    def __init__(self, pipes):
        self.pipes = pipes
        self.R = len(pipes)
        self.C = len(pipes[0])
        start = "".join(pipes).index("S")
        self.start_pos = (start // self.C, start % self.C)
        self.loop = [self.start_pos]
        self.discarded = set()
        self.in_loop = set(self.loop)
        self.inner_tiles = set()
        self.loop_found = False
        self.turn = 0

    def get_neighbour(self, r, c, direction):
        dr, dc = movechars_dr_dc[direction]
        neighbour_r = r + dr
        neighbour_c = c + dc
        if neighbour_r >= self.R or neighbour_r < 0:
            return None
        if neighbour_c >= self.C or neighbour_c < 0:
            return None
        neighbour = self.pipes[neighbour_r][neighbour_c]

        if opposite[direction] in directions[neighbour]:
            return (neighbour_r, neighbour_c)
        return None

    def is_in_loop(self, position):
        return position in self.in_loop

    def update(self, turn):
        while self.turn < turn and not self.loop_found:
            self.turn += 1
            # while not (loop[-1] == (r_start, c_start) and len(loop) > 1):
            came_from = None if len(self.loop) <= 1 else self.loop[-2]
            r, c = self.loop[-1]
            symbol = self.pipes[r][c]
            symbol_dirs = directions[symbol]
            for dir in symbol_dirs:
                neighbour = self.get_neighbour(r, c, dir)
                if (
                    neighbour == came_from
                    or neighbour is None
                    or neighbour in self.discarded
                ):
                    continue
                self.loop.append(neighbour)
                self.in_loop.add(neighbour)
                break
            if self.loop[-1] == (r, c):
                # we could not go anywhere
                position = self.loop.pop()
                self.discarded.add(position)
                self.in_loop.discard(position)
            if self.loop[0] == self.loop[-1]:
                self.loop_found = True
                self._locate_inner_tiles()

    def _locate_inner_tiles(self):
        # first find out which pipe type is at the S point
        sr, sc = self.loop[0]
        neighbour1 = self.loop[1]
        neighbour2 = self.loop[-2]
        sdirections = ""
        for nr, nc in [neighbour1, neighbour2]:
            if sr == nr:
                sdirections += ">" if nc > sc else "<"
            else:
                sdirections += "v" if nr > sr else "^"
        s_symbol = next(
            char
            for char, dirs in directions.items()
            if sorted(dirs) == sorted(sdirections)
        )
        self.pipes[sr] = self.pipes[sr].replace("S", s_symbol)
        for r, line in enumerate(self.pipes):
            out = True
            for c, char in enumerate(line):
                if self.is_in_loop((r, c)):
                    if char in "|LJ":
                        out = not out
                elif not out:
                    self.inner_tiles.add((r, c))

    def reset(self):
        self.loop = [self.start_pos]
        self.discarded = set()
        self.in_loop = set(self.loop)
        self.inner_tiles = set()
        self.loop_found = False
        self.turn = 0


def make_tiles(tile_size: int, color):
    if tile_size <= 2:
        raise ValueError(f"Tiles need at least 3 pixels, you asked for {tile_size}px")
    pipe_width = tile_size // 3
    if tile_size % 2 != pipe_width % 2:
        pipe_width += 1
    padding = (tile_size - pipe_width) // 2
    if padding > 1:
        padding -= 1
        pipe_width += 2
    assert pipe_width + 2 * padding == tile_size

    tiles = {}
    for tile in ".-|JL7FS":
        surf = pg.Surface((tile_size, tile_size))
        surf.fill(BACKGROUND)
        pg.draw.rect(surf, color, pg.Rect(padding, padding, pipe_width, pipe_width))
        for direction in directions[tile]:
            match direction:
                case ">":
                    pg.draw.rect(
                        surf,
                        color,
                        pg.Rect(padding + pipe_width, padding, padding, pipe_width),
                    )
                case "<":
                    pg.draw.rect(surf, color, pg.Rect(0, padding, padding, pipe_width))
                case "v":
                    pg.draw.rect(
                        surf,
                        color,
                        pg.Rect(padding, padding + pipe_width, pipe_width, padding),
                    )
                case "^":
                    pg.draw.rect(surf, color, pg.Rect(padding, 0, pipe_width, padding))
        tiles[tile] = surf
    return tiles, pipe_width


def run():
    # Get sizes from input data
    text_input = get_data(year=2023, day=10)
    pipes = text_input.split("\n")
    maze = PipeMaze(pipes)
    R = len(pipes)
    C = len(pipes[0])
    tile_size = min(WIDTH // C, HEIGHT // R)
    tiles = {}
    for color in (TEXT_COLOR, SILVER, GOLD, GREY_COLOR):
        tiles[color], pipe_width = make_tiles(tile_size, color)
    W0 = (WIDTH - C * tile_size) // 2
    H0 = (HEIGHT - R * tile_size) // 2
    print(f"tile size {tile_size} pipe_width {pipe_width}")

    def get_rect(r, c):
        return pg.Rect(W0 + c * tile_size, H0 + r * tile_size, tile_size, tile_size)

    pg.init()
    screen = pg.display.set_mode([WIDTH, HEIGHT])
    pg.display.set_caption("Advent of Code 2023 - Day 10 - Pipe Maze")

    clock = pg.time.Clock()

    t0 = time.perf_counter()
    running = True
    t_part2 = 0
    highlight_up_to = 0
    # main loop
    while running:
        clock.tick(FPS)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                t0 = time.perf_counter()  # reset to start
                maze.reset()
                t_part2 = 0
                highlight_up_to = 0

        t = max(0, time.perf_counter() - t0 - INITIAL_DELAY)
        if maze.loop_found:
            highlight_up_to = C * min(1, (t - t_part2) / 5)
        else:
            turn = t * 200
            maze.update(turn)
            t_part2 = t

        # erase everything
        screen.fill(BACKGROUND)
        # render maze
        for r, line in enumerate(pipes):
            for c, char in enumerate(line):
                color = TEXT_COLOR
                if maze.is_in_loop((r, c)):
                    color = SILVER
                elif maze.loop_found and c < highlight_up_to:
                    if (r, c) in maze.inner_tiles:
                        color = GOLD
                    else:
                        color = GREY_COLOR
                screen.blit(tiles[color][char], get_rect(r, c))
        # actually update the screen now
        pg.display.flip()

    pg.quit()
    sys.exit()


if __name__ == "__main__":
    run()
