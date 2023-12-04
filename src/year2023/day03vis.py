# Problem statement: https://adventofcode.com/2023/day/3

import sys
import pygame as pg
from aocd import get_data
import time
import re
from dataclasses import dataclass
from collections import defaultdict

SILVER = (153, 153, 204)
GOLD = (230, 230, 94)
TEXT_COLOR = (204, 204, 204)
BACKGROUND = (15, 15, 35)
BACKGROUND_2 = (25, 25, 55)

WIDTH = 1280
HEIGHT = 720
TOTALS_HEIGHT = 60

FPS = 60
INITIAL_DELAY = 2
TIME_PER_TURN = 0.2
GOLD_DELAY = 15  # turns


@dataclass
class Span:
    start: int
    end: int
    text: str
    is_dots: bool = False
    is_num: bool = False
    is_part_number: bool = False
    is_gear_ratio: bool = False
    is_symbol: bool = False
    is_gear: bool = False
    gear_ratio: int = 0


def annotate(text_input):
    lines = text_input.split("\n")
    potential_gears = defaultdict(list)
    gear_values = defaultdict(list)
    part_numbers = set()
    for i, line in enumerate(lines):
        start_line = max(i - 1, 0)
        end_line = min(i + 2, len(lines))
        for match in re.finditer(r"(\d+)", line):
            start_check = max(0, match.start() - 1)
            end_check = min(len(line), match.end() + 1)
            is_part_number = False
            for l in range(start_line, end_line):
                for c in range(start_check, end_check):
                    if lines[l][c] == "*":
                        potential_gears[(l, c)].append((i, match.start()))
                        gear_values[(l, c)].append(int(match.group()))
                    if (
                        not is_part_number
                        and lines[l][c] != "."
                        and not lines[l][c].isnumeric()
                    ):
                        is_part_number = True
            if is_part_number:
                part_numbers.add((i, match.start()))
    gears = {loc: nums for loc, nums in potential_gears.items() if len(nums) == 2}
    gear_positions = set(position for nums in gears.values() for position in nums)
    gear_ratios = {
        loc: gear_values[loc][0] * gear_values[loc][1] for loc in gears.keys()
    }

    line_matches = list(re.finditer(r"(\d+|\.+|[^\.\d])", line) for line in lines)
    annotated_lines = []
    for i, line in enumerate(line_matches):
        annotated_line = []
        for m, match in enumerate(line):
            text = match.group()
            position = (i, match.start())
            if text[0].isnumeric():
                annotated_line.append(
                    Span(
                        match.start(),
                        match.end(),
                        text,
                        is_num=True,
                        is_part_number=position in part_numbers,
                        is_gear_ratio=position in gear_positions,
                    )
                )
            elif text[0] == ".":
                annotated_line.append(
                    Span(
                        match.start(),
                        match.end(),
                        text,
                        is_dots=True,
                    )
                )
            elif text[0] == "*":
                annotated_line.append(
                    Span(
                        match.start(),
                        match.end(),
                        text,
                        is_symbol=True,
                        is_gear=position in gears,
                        gear_ratio=gear_ratios.get(position, 0),
                    )
                )
            else:
                annotated_line.append(
                    Span(
                        match.start(),
                        match.end(),
                        text,
                        is_symbol=True,
                    )
                )
        annotated_lines.append(annotated_line)
    return annotated_lines


def run():
    # Get sizes from input data
    text_input = get_data(year=2023, day=3)
    lines = text_input.split("\n")
    NUM_LINES = len(lines)
    NUM_CHARS = len(lines[0])
    print(NUM_LINES, "lines,", NUM_CHARS, "chars")

    annotated_lines = annotate(text_input)

    pg.init()
    screen = pg.display.set_mode([WIDTH, HEIGHT])
    pg.display.set_caption("Advent of Code 2023 - Day 3 - Gear Ratios")
    font = pg.font.SysFont("monospace", 14)
    symbol = font.render(".", 1, TEXT_COLOR)
    symbol_rect = symbol.get_rect()
    PADDING = (WIDTH - NUM_CHARS * symbol_rect.width) // 2
    if PADDING < 0:
        raise ValueError("Use a smaller font size so whole lines fit the screen")

    clock = pg.time.Clock()

    t0 = time.perf_counter()
    running = True

    while running:
        clock.tick(FPS)

        t = time.perf_counter() - t0
        silver_lines = min(
            len(lines) + 1, int(max(0, t - INITIAL_DELAY) / TIME_PER_TURN)
        )
        gold_lines = min(
            len(lines) + 1,
            int(max(0, t - INITIAL_DELAY - TIME_PER_TURN * GOLD_DELAY) / TIME_PER_TURN),
        )
        dt = max(0, t - INITIAL_DELAY - silver_lines * TIME_PER_TURN)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                t0 = time.perf_counter()

        # erase everything
        screen.fill(BACKGROUND)

        scrolled = min(
            max(0, silver_lines - 30) * symbol_rect.height,
            (len(lines)) * symbol_rect.height - HEIGHT + PADDING + 100,
        )
        # dh = min(len(lines), max(0, silver_lines - 30)) * symbol_rect.height
        dh = 0
        if (
            scrolled > 0
            and scrolled < (len(lines)) * symbol_rect.height - HEIGHT + PADDING + 100
        ):
            dh = -(dt / TIME_PER_TURN) * symbol_rect.height

        total_1 = 0
        total_2 = 0

        for i, line in enumerate(annotated_lines):
            if i < gold_lines:
                # show annotated for part 2
                for s, span in enumerate(line):
                    total_2 += span.gear_ratio
                    if span.is_part_number:
                        total_1 += int(span.text)
                    color = TEXT_COLOR
                    background = BACKGROUND
                    if span.is_gear or span.is_gear_ratio:
                        color = GOLD
                        background = BACKGROUND_2

                    alpha = 255
                    if (
                        span.is_dots
                        or (span.is_num and not span.is_gear_ratio)
                        or (span.is_symbol and not span.is_gear)
                    ):
                        alpha = 128

                    text = font.render(span.text, 1, color, background)
                    text.set_alpha(alpha)
                    rect = text.get_rect(
                        left=PADDING + span.start * symbol_rect.width,
                        top=PADDING - scrolled + dh + i * symbol_rect.height,
                    )
                    screen.blit(text, rect)
            elif i < silver_lines:
                # show annotated for part 1
                for s, span in enumerate(line):
                    color = TEXT_COLOR
                    background = BACKGROUND
                    if span.is_part_number or span.is_symbol:
                        color = SILVER
                        background = BACKGROUND_2
                    if span.is_part_number:
                        total_1 += int(span.text)

                    alpha = 255
                    if span.is_dots or (span.is_num and not span.is_part_number):
                        alpha = 128

                    text = font.render(span.text, 1, color, background)
                    text.set_alpha(alpha)
                    rect = text.get_rect(
                        left=PADDING + span.start * symbol_rect.width,
                        top=PADDING - scrolled + dh + i * symbol_rect.height,
                    )
                    screen.blit(text, rect)
            else:
                # show raw line
                text = font.render(lines[i], 1, TEXT_COLOR)
                rect = text.get_rect(
                    left=PADDING,
                    top=PADDING - scrolled + dh + i * symbol_rect.height,
                )
                screen.blit(text, rect)

        # render totals
        text = font.render("> " + str(total_1), 1, SILVER, BACKGROUND_2)
        rect = text.get_rect(
            left=PADDING + NUM_CHARS * symbol_rect.width,
            top=PADDING - scrolled + silver_lines * symbol_rect.height,
        )
        screen.blit(text, rect)

        text = font.render("> " + str(total_2), 1, GOLD, BACKGROUND_2)
        rect = text.get_rect(
            left=PADDING + NUM_CHARS * symbol_rect.width,
            top=PADDING - scrolled + (gold_lines - 1) * symbol_rect.height,
        )
        screen.blit(text, rect)

        # actually update the screen now
        pg.display.flip()

    pg.quit()
    sys.exit()


if __name__ == "__main__":
    run()
