# Problem statement: https://adventofcode.com/2023/day/5

import sys
import pygame as pg
from aocd import get_data
import time
from dataclasses import dataclass
from year2023.day05 import parse_input, AlmanacMap
from util.segments import Segment1D, Segment1DCollection

SILVER = (153, 153, 204)
GOLD = (230, 230, 94)
TEXT_COLOR = (204, 204, 204)
BACKGROUND = (15, 15, 35)
BACKGROUND_2 = (25, 25, 55)

WIDTH = 1280
HEIGHT = 720
W_PADDING = 50

FPS = 60
INITIAL_DELAY = 2
TIME_PER_TURN = 4
DOT_RADIUS = 5
GOLD_LINE_WIDTH = 3


@dataclass
class Stage:
    source_points: list[int]
    source_ranges: list["Segment1D"]
    almanac_map: AlmanacMap
    destination_ranges: list["Segment1D"]
    destination_points: list[int]
    source_label: str
    destination_label: str


def annotate(text_input):
    seeds, almanac, sequence = parse_input(text_input)
    stages = []
    item = "seed"
    source_points = seeds
    source_ranges = sorted(
        Segment1D(start, start + length - 1)
        for start, length in zip(seeds[0::2], seeds[1::2])
    )
    while item != "location":
        alm = almanac[item]
        # we need to split up source ranges into portions by the path they will follow
        adapted_source = []
        adapted_destination = {}
        collection = Segment1DCollection(
            source_ranges
        )  # this sorts and defragments segments
        todo = list(collection.segments)
        while len(todo) > 0:
            segment = todo.pop()
            found = False
            for r in alm.ranges:
                res, left = r.transform_range(segment)
                if len(res) > 0:
                    found = True
                    dest_segment = res[0]
                    source_segment = Segment1D(
                        dest_segment.a - r.delta, dest_segment.b - r.delta
                    )
                    adapted_source.append(source_segment)
                    adapted_destination[source_segment] = dest_segment
                    todo.extend(left)
                    break
            if not found:
                adapted_source.append(segment)
        adapted_source.sort()
        source_points = sorted(source_points)
        destination_points = [alm.transform_point(p) for p in source_points]
        stages.append(
            Stage(
                source_points=list(source_points),
                source_ranges=list(adapted_source),
                destination_points=list(destination_points),
                destination_ranges=[
                    adapted_destination.get(s, s) for s in adapted_source
                ],
                almanac_map=almanac[item],
                source_label=item,
                destination_label=sequence[item],
            )
        )
        source_points = destination_points
        item = sequence[item]
        source_ranges = [adapted_destination.get(s, s) for s in adapted_source]

    return stages


def run():
    # Get sizes from input data
    text_input = get_data(year=2023, day=5)
    stages = annotate(text_input)
    print(min(stages[-1].destination_points))
    pg.init()
    screen = pg.display.set_mode([WIDTH, HEIGHT])
    pg.display.set_caption(
        "Advent of Code 2023 - Day 5 - If You Give A Seed A Fertilizer"
    )

    font = pg.font.SysFont("monospace", 16)
    clock = pg.time.Clock()

    t0 = time.perf_counter()
    running = True

    N = len(stages)

    DH = HEIGHT // (N + 1)

    def y_pixels(n):
        return DH // 2 + DH * n

    def x_pixels(n):
        return W_PADDING + (WIDTH - 2 * W_PADDING) * (n / 5_000_000_000)

    # prepare background
    background = pg.Surface((WIDTH, HEIGHT))
    background.fill(BACKGROUND)
    paths = pg.Surface((WIDTH, HEIGHT))

    for i, stage in enumerate(stages):
        for r in stage.almanac_map.ranges:
            paths.fill((0, 0, 0, 0))
            rect = pg.draw.polygon(
                paths,
                (20, 20, 20),
                [
                    (x_pixels(r.segment.a), y_pixels(i)),
                    (x_pixels(r.segment.a + r.delta), y_pixels(i + 1)),
                    (x_pixels(r.segment.b + r.delta), y_pixels(i + 1)),
                    (x_pixels(r.segment.b), y_pixels(i)),
                ],
            )
            background.blit(paths, rect, rect, pg.BLEND_ADD)
    del paths
    # draw horizontal lines
    for i in range(N + 1):
        pg.draw.line(
            background,
            TEXT_COLOR,
            (W_PADDING, y_pixels(i)),
            (WIDTH - W_PADDING, y_pixels(i)),
            1,
        )
        # add text label
        label = (
            stages[i].source_label if i < len(stages) else stages[-1].destination_label
        )
        text = font.render(label, 1, TEXT_COLOR)
        rect = text.get_rect(bottom=y_pixels(i), right=WIDTH - W_PADDING)
        background.blit(text, rect)

    # main loop
    while running:
        clock.tick(FPS)

        t = time.perf_counter() - t0
        current_turn = min(2 * N + 1, int(max(0, t - INITIAL_DELAY) / TIME_PER_TURN))
        dt = max(0, t - INITIAL_DELAY - current_turn * TIME_PER_TURN) / TIME_PER_TURN
        dt = min(dt, 1)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                t0 = time.perf_counter()

        # erase everything
        screen.blit(background, screen.get_rect())

        if current_turn < N:
            # part 1 animation - silver points
            # show initial state
            if dt < 0.05:
                for point in stages[current_turn].source_points:
                    pg.draw.circle(
                        screen,
                        SILVER,
                        (x_pixels(point), y_pixels(current_turn)),
                        DOT_RADIUS,
                    )
            elif dt < 0.95:
                # show movement
                S = len(stages[current_turn].source_points) - 1
                for i, (ps, pd) in enumerate(
                    zip(
                        stages[current_turn].source_points,
                        stages[current_turn].destination_points,
                    )
                ):
                    sx = x_pixels(ps)
                    dx = x_pixels(pd)
                    sy = y_pixels(current_turn)
                    dy = y_pixels(current_turn + 1)
                    degree_moved = (dt - 0.05) / 0.9
                    degree_moved = min(1, max(0, 5 * degree_moved - 4 * (i / S)))
                    x = sx * (1 - degree_moved) + dx * degree_moved
                    y = sy * (1 - degree_moved) + dy * degree_moved
                    pg.draw.circle(screen, SILVER, (x, y), DOT_RADIUS)
                    pg.draw.aaline(screen, SILVER, (sx, sy), (dx, dy))
            else:
                # show final state
                for point in stages[current_turn].destination_points:
                    pg.draw.circle(
                        screen,
                        SILVER,
                        (x_pixels(point), y_pixels(current_turn + 1)),
                        DOT_RADIUS,
                    )
        elif current_turn == N:
            # final stage of part 1, animate convergence to minimum
            min_point = min(stages[-1].destination_points)
            minx = x_pixels(min_point)
            miny = y_pixels(N)
            for point in stages[-1].destination_points:
                x = x_pixels(point)
                dx = (x - minx) / (WIDTH - 2 * W_PADDING) - 2 * (x == minx)
                if dx < 1 - dt:
                    pg.draw.circle(
                        screen,
                        SILVER,
                        (x, miny),
                        DOT_RADIUS,
                    )
            # show stationary segments on top floor
            for segment in stages[0].source_ranges:
                pg.draw.line(
                    screen,
                    GOLD,
                    (x_pixels(segment.a), y_pixels(0)),
                    (x_pixels(segment.b), y_pixels(0)),
                    2,
                )
        elif current_turn < 2 * N + 1:
            # keep part 1 answer
            min_point = min(stages[-1].destination_points)
            minx = x_pixels(min_point)
            miny = y_pixels(N)
            pg.draw.circle(
                screen,
                SILVER,
                (minx, miny),
                DOT_RADIUS,
            )
            # begin part 2
            current_index = current_turn - N - 1
            stage = stages[current_index]
            # show initial state
            if dt < 0.1:
                for segment in stage.source_ranges:
                    pg.draw.line(
                        screen,
                        GOLD,
                        (x_pixels(segment.a), y_pixels(current_index)),
                        (x_pixels(segment.b), y_pixels(current_index)),
                        GOLD_LINE_WIDTH,
                    )
            elif dt < 0.95:
                # show movement
                S = len(stage.source_ranges) - 1
                for i, (rs, rd) in enumerate(
                    zip(
                        stage.source_ranges,
                        stage.destination_ranges,
                    )
                ):
                    sxa, sxb = x_pixels(rs.a), x_pixels(rs.b)
                    dxa, dxb = x_pixels(rd.a), x_pixels(rd.b)
                    sy = y_pixels(current_index)
                    dy = y_pixels(current_index + 1)
                    degree_moved = (dt - 0.05) / 0.9
                    degree_moved = min(1, max(0, 5 * degree_moved - 4 * (i / S)))
                    xa = sxa * (1 - degree_moved) + dxa * degree_moved
                    xb = sxb * (1 - degree_moved) + dxb * degree_moved
                    y = sy * (1 - degree_moved) + dy * degree_moved
                    pg.draw.line(
                        screen,
                        GOLD,
                        (xa, y),
                        (xb, y),
                        GOLD_LINE_WIDTH,
                    )
            else:
                for segment in stage.destination_ranges:
                    pg.draw.line(
                        screen,
                        GOLD,
                        (x_pixels(segment.a), y_pixels(current_index + 1)),
                        (x_pixels(segment.b), y_pixels(current_index + 1)),
                        GOLD_LINE_WIDTH,
                    )
        else:
            # final stage of part 2
            # keep part 1 answer
            min_point = min(stages[-1].destination_points)
            minx = x_pixels(min_point)
            miny = y_pixels(N)
            pg.draw.circle(
                screen,
                SILVER,
                (minx, miny),
                DOT_RADIUS,
            )
            # animate gold convergence
            min_point = min(s.a for s in stages[-1].destination_ranges)
            minx = x_pixels(min_point)
            xmax = minx + (1 - dt) * (WIDTH - 2 * W_PADDING)
            for segment in stages[-1].destination_ranges:
                xa = x_pixels(segment.a)
                xb = x_pixels(segment.b)
                if xa < xmax:
                    pg.draw.line(
                        screen,
                        GOLD,
                        (xa, miny),
                        (min(xb, xmax), miny),
                        GOLD_LINE_WIDTH,
                    )
            if dt > 0.5:
                pg.draw.circle(
                    screen,
                    GOLD,
                    (minx, miny),
                    DOT_RADIUS * (dt - 0.5) * 2,
                )

        # actually update the screen now
        pg.display.flip()

    pg.quit()
    sys.exit()


if __name__ == "__main__":
    run()
