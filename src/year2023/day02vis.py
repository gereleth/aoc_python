# Problem statement: https://adventofcode.com/2023/day/2

import sys
import pygame as pg
from aocd import get_data
import time
import re
from functools import lru_cache
from dataclasses import dataclass

SILVER = (153, 153, 204)
GOLD = (230, 230, 94)
TEXT_COLOR = (204, 204, 204)
BACKGROUND = (15, 15, 35)
BACKGROUND_2 = (25, 25, 55)
RED = (200, 60, 60)
GREEN = (60, 200, 60)
BLUE = (60, 60, 200)

WIDTH = 1280
HEIGHT = 720
TOTALS_HEIGHT = 60

FPS = 60
INITIAL_DELAY = 2
TIME_PER_TURN = 1
CUBES_APPEAR_TIME = 0.5 * TIME_PER_TURN
SCORE_UPDATE_TIME = 0.9 * TIME_PER_TURN

LIMIT = {"red": 12, "green": 13, "blue": 14}
colors = {"red": RED, "green": GREEN, "blue": BLUE}


@dataclass
class Game:
    game_id: int
    rounds: list[dict]
    max_counts: dict
    score_1: int
    score_2: int


@dataclass
class State:
    total_1: int
    total_2: int
    game: Game


def run():
    # Get sizes from input data
    text_input = get_data(year=2023, day=2)
    lines = text_input.split("\n")
    NUM_GAMES = len(lines)
    MAX_ROUNDS = max(line.count(";") + 1 for line in lines)
    MAX_CUBES = (
        max(int(i) for line in lines for i in re.findall(r"\d+", line.split(": ")[1]))
        + 1
    )
    ROUND_WIDTH = WIDTH // MAX_ROUNDS
    PADDING = 30
    CUBE_WIDTH = (ROUND_WIDTH - 4 * PADDING) // len(LIMIT)
    CUBE_HEIGHT = (HEIGHT - TOTALS_HEIGHT - PADDING) // MAX_CUBES
    print(
        NUM_GAMES,
        "games,",
        MAX_ROUNDS,
        "rounds,",
        MAX_CUBES,
        "cubes",
        f"w{CUBE_WIDTH} h{CUBE_HEIGHT}",
    )

    @lru_cache(maxsize=5)
    def game_state_at_turn(n):
        line = lines[n]
        game, rounds = line.split(": ")
        game_id = int(game.split()[1])
        game_rounds = []
        is_possible = True
        max_counts = {k: 0 for k in LIMIT.keys()}
        for balls in rounds.split("; "):
            game_round = {}
            for ball in balls.split(", "):
                count, color = ball.split()
                count = int(count)
                game_round[color] = count
                if count > LIMIT[color]:
                    is_possible = False
                max_counts[color] = max(max_counts[color], count)
            game_rounds.append(game_round)
        score_1 = game_id if is_possible else 0
        score_2 = 1
        for count in max_counts.values():
            score_2 *= count
        game = Game(
            game_id=game_id,
            rounds=game_rounds,
            max_counts=max_counts,
            score_1=score_1,
            score_2=score_2,
        )
        if n == 0:
            return State(total_1=0, total_2=0, game=game)
        else:
            prev_state = game_state_at_turn(n - 1)
            return State(
                total_1=prev_state.total_1 + prev_state.game.score_1,
                total_2=prev_state.total_2 + prev_state.game.score_2,
                game=game,
            )

    pg.init()
    screen = pg.display.set_mode([WIDTH, HEIGHT])
    pg.display.set_caption("Advent of Code 2023 - Day 2 - Cube Conundrum")
    font_big = pg.font.SysFont("monospace", 30)
    font_small = pg.font.SysFont("monospace", 20)
    clock = pg.time.Clock()

    area_totals_1 = screen.subsurface(pg.Rect(0, 0, WIDTH // 2, TOTALS_HEIGHT))
    area_totals_2 = screen.subsurface(pg.Rect(WIDTH // 2, 0, WIDTH // 2, TOTALS_HEIGHT))
    area_game = screen.subsurface(
        pg.Rect(0, TOTALS_HEIGHT, WIDTH, HEIGHT - TOTALS_HEIGHT)
    )

    part_1_label = font_big.render("Part 1: ", 1, SILVER)
    part_2_label = font_big.render("Part 2: ", 1, GOLD)

    # predraw some cubes
    cubes = {}
    for color in LIMIT.keys():
        cube = pg.Surface((CUBE_WIDTH, CUBE_HEIGHT))
        cube.fill(BACKGROUND)
        pg.draw.rect(
            cube, colors[color], pg.Rect(0, 0, CUBE_WIDTH - 2, CUBE_HEIGHT - 2), 0, 3
        )
        cube.set_alpha(192)
        cubes[color] = cube

    t0 = time.perf_counter()
    running = True

    while running:
        clock.tick(FPS)

        t = time.perf_counter() - t0
        turn = min(len(lines) - 1, int(max(0, t - INITIAL_DELAY) / TIME_PER_TURN))
        dt = max(0, t - INITIAL_DELAY - turn * TIME_PER_TURN)
        state = game_state_at_turn(turn)
        game = state.game

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        # erase everything
        screen.fill(BACKGROUND)

        # render part 1 running total
        area_totals_1.blit(
            part_1_label,
            part_1_label.get_rect(centery=TOTALS_HEIGHT // 2, right=WIDTH // 4),
        )
        total_1 = state.total_1 + (game.score_1 if dt > SCORE_UPDATE_TIME else 0)
        part_1_value = font_big.render(str(total_1), 1, SILVER)
        part_1_value_rect = part_1_label.get_rect(
            centery=TOTALS_HEIGHT // 2, left=WIDTH // 4
        )
        area_totals_1.blit(
            part_1_value,
            part_1_value_rect,
        )

        # render part 2 running total
        area_totals_2.blit(
            part_2_label,
            part_2_label.get_rect(centery=TOTALS_HEIGHT // 2, right=WIDTH // 4),
        )
        total_2 = state.total_2 + (game.score_2 if dt > SCORE_UPDATE_TIME else 0)
        part_2_value = font_big.render(str(total_2), 1, GOLD)
        part_2_value_rect = part_2_label.get_rect(
            centery=TOTALS_HEIGHT // 2, left=WIDTH // 4
        )
        area_totals_2.blit(
            part_2_value,
            part_2_value_rect,
        )

        # zebra-color even rounds
        for i in range(MAX_ROUNDS):
            x_round = i * ROUND_WIDTH
            if i % 2 == 0:
                pg.draw.rect(
                    area_game,
                    BACKGROUND_2,
                    pg.Rect(x_round, 0, ROUND_WIDTH, HEIGHT - TOTALS_HEIGHT),
                )

        max_count_labels = {}

        # render game rounds
        for i, game_round in enumerate(game.rounds):
            x_round = i * ROUND_WIDTH
            # draw colored stacks
            for c, color in enumerate(LIMIT.keys()):
                x_color = PADDING + c * (PADDING + CUBE_WIDTH)
                count = game_round.get(color, 0)
                if count == 0:
                    continue

                # draw cubes
                for b in range(count):
                    if b < dt * MAX_CUBES / CUBES_APPEAR_TIME:
                        area_game.blit(
                            cubes[color],
                            (
                                x_round + x_color,
                                PADDING + CUBE_HEIGHT * (MAX_CUBES - b - 1),
                            ),
                        )

                # draw limit line if over limit
                if (
                    count > LIMIT[color]
                    and count - 1 < dt * MAX_CUBES / CUBES_APPEAR_TIME
                ):
                    y_line = PADDING + CUBE_HEIGHT * (MAX_CUBES - LIMIT[color]) - 2
                    pg.draw.line(
                        area_game,
                        SILVER,
                        (x_round + x_color - PADDING, y_line),
                        (x_round + x_color + CUBE_WIDTH + PADDING, y_line),
                        2,
                    )

                # render max count text
                if (
                    count == game.max_counts[color]
                    and count < dt * MAX_CUBES / CUBES_APPEAR_TIME
                    and color not in max_count_labels
                ):
                    label = font_small.render(str(count), 1, GOLD)
                    rect = label.get_rect(
                        centerx=x_round + x_color + CUBE_WIDTH // 2,
                        top=TOTALS_HEIGHT
                        + PADDING
                        + CUBE_HEIGHT * (MAX_CUBES - count - 1),
                    )
                    max_count_labels[color] = (label, rect)
                    screen.blit(label, rect)

        # render game label
        game_label = font_big.render(f"Game {game.game_id}", 1, TEXT_COLOR)
        game_label_rect = game_label.get_rect(centerx=WIDTH // 2, top=0)
        area_game.blit(game_label, game_label_rect)

        # render flying label 1
        if dt > CUBES_APPEAR_TIME and dt < TIME_PER_TURN:
            moved_degree = min(
                1,
                max(0, (dt - CUBES_APPEAR_TIME) / (TIME_PER_TURN - CUBES_APPEAR_TIME)),
            )
            if game.score_1 > 0:
                # render flying label 1
                fly_score_1 = font_big.render(f"{game.game_id}", 1, SILVER)
                rect_1 = fly_score_1.get_rect(
                    right=game_label_rect.right,
                    centery=TOTALS_HEIGHT + game_label_rect.centery,
                )
                rect_2 = fly_score_1.get_rect(
                    top=part_1_value_rect.centery, left=part_1_value_rect.centerx
                )
                rect_2.top = rect_2.top * moved_degree + rect_1.top * (1 - moved_degree)
                rect_2.left = rect_2.left * moved_degree + rect_1.left * (
                    1 - moved_degree
                )
                screen.blit(fly_score_1, rect_2)

            # render flying label2s
            for color, (label, rect_1) in max_count_labels.items():
                rect_2 = label.get_rect(
                    top=part_2_value_rect.centery,
                    centerx=part_2_value_rect.centerx + WIDTH // 2,
                )
                rect_2.top = rect_2.top * moved_degree + rect_1.top * (1 - moved_degree)
                rect_2.left = rect_2.left * moved_degree + rect_1.left * (
                    1 - moved_degree
                )
                screen.blit(label, rect_2)

        # actually update the screen now
        pg.display.flip()

    pg.quit()
    sys.exit()


if __name__ == "__main__":
    run()
