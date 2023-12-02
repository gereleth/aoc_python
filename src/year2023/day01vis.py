# Problem statement: https://adventofcode.com/2023/day/1

from math import ceil
import sys
import pygame as pg
from aocd import get_data
import time
import re
from functools import lru_cache

day_title = "Trebuchet?!"

SILVER = (153, 153, 204)
GOLD = (230, 230, 94)
TEXT_COLOR = (204, 204, 204)
BACKGROUND = (15, 15, 35)

WIDTH = 960
HEIGHT = 720
TEXT_ROW_HEIGHT = 90
HEIGHT_MIDDLE = HEIGHT // 2 + TEXT_ROW_HEIGHT
NUM_ROWS = ceil(HEIGHT / TEXT_ROW_HEIGHT)
PADDING = 20
FPS = 60
SCROLL_SPEED = 1


# cached to reuse the same surface while it floats up the screen
@lru_cache(maxsize=NUM_ROWS)
def draw_text(text, font):
    surface = pg.Surface(size=(WIDTH, TEXT_ROW_HEIGHT))
    surface.fill(BACKGROUND)
    line = font.render(text, 1, TEXT_COLOR)
    rect = line.get_rect(centerx=WIDTH // 2, centery=TEXT_ROW_HEIGHT // 2)
    surface.blit(line, dest=rect)
    return surface


def spans_part_1(line):
    res = ""
    digits = list(re.finditer(r"(\d)", line))
    first, last = digits[0], digits[-1]
    res = first.group() + last.group()
    return [(first.start(), first.end()), (last.start(), last.end())], res


spelled_numbers = "one two three four five six seven eight nine"
spelled_to_digit = {x: str(i + 1) for i, x in enumerate(spelled_numbers.split())}
pattern = "|".join(spelled_numbers.split() + [r"\d"])
expr = re.compile(f"(?=({pattern}))")


def spans_part_2(line):
    digit_likes = list(re.finditer(expr, line))
    first = digit_likes[0]
    last = digit_likes[-1]
    spans = [(first.start(1), first.end(1)), (last.start(1), last.end(1))]
    num1 = spelled_to_digit.get(first.group(1), first.group(1))
    num2 = spelled_to_digit.get(last.group(1), last.group(1))
    return spans, num1 + num2


@lru_cache(maxsize=NUM_ROWS)
def draw_annotated_text(text, font):
    surface = pg.Surface(size=(WIDTH, TEXT_ROW_HEIGHT))
    surface.fill(BACKGROUND)
    line = font.render(text, 1, TEXT_COLOR)
    rect = line.get_rect(centerx=WIDTH // 2, centery=TEXT_ROW_HEIGHT // 2)
    surface.blit(line, dest=rect)

    # Part 1 annotations below the line
    spans1, result1 = spans_part_1(text)
    for span in spans1:
        start = rect.left + rect.width * span[0] / len(text)
        end = rect.left + rect.width * span[1] / len(text)
        pg.draw.line(
            surface,
            SILVER,
            (start, TEXT_ROW_HEIGHT - PADDING),
            (end, TEXT_ROW_HEIGHT - PADDING),
            2,
        )
        pg.draw.line(
            surface,
            SILVER,
            (start, TEXT_ROW_HEIGHT - PADDING),
            (start, TEXT_ROW_HEIGHT - int(PADDING * 1.3)),
            2,
        )
        pg.draw.line(
            surface,
            SILVER,
            (end, TEXT_ROW_HEIGHT - PADDING),
            (end, TEXT_ROW_HEIGHT - int(PADDING * 1.3)),
            2,
        )
    result_text = font.render(result1, 1, SILVER)
    result_rect = result_text.get_rect(
        right=TEXT_ROW_HEIGHT // 2, centery=TEXT_ROW_HEIGHT // 2
    )
    surface.blit(result_text, dest=result_rect)

    # Part 2 annotations above the line
    spans2, result2 = spans_part_2(text)
    for span in spans2:
        start = rect.left + rect.width * span[0] / len(text)
        end = rect.left + rect.width * span[1] / len(text)
        pg.draw.line(surface, GOLD, (start, PADDING), (end, PADDING), 2)
        pg.draw.line(
            surface,
            GOLD,
            (start, PADDING),
            (start, int(PADDING * 1.3)),
            2,
        )
        pg.draw.line(surface, GOLD, (end, PADDING), (end, int(PADDING * 1.3)), 2)
    result_text = font.render(result2, 1, GOLD)
    result_rect = result_text.get_rect(
        left=WIDTH - TEXT_ROW_HEIGHT // 2, centery=TEXT_ROW_HEIGHT // 2
    )
    surface.blit(result_text, dest=result_rect)
    return surface


def run():
    pg.init()
    screen = pg.display.set_mode([WIDTH, HEIGHT])
    pg.display.set_caption("Advent of Code 2023 - Day 1 - Trebuchet?!")
    font = pg.font.SysFont("monospace", int(0.3 * TEXT_ROW_HEIGHT))
    clock = pg.time.Clock()

    scroll_speed = SCROLL_SPEED
    text_input = get_data(year=2023, day=1)
    lines = text_input.split("\n")
    h = 0
    last_idx = -1
    result1 = 0
    result2 = 0

    t0 = time.perf_counter()
    running = True
    while running:
        clock.tick(FPS)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        # erase everything
        screen.fill(BACKGROUND)
        idx = h // TEXT_ROW_HEIGHT
        dh = h % TEXT_ROW_HEIGHT
        # render middle line text
        if idx < len(lines):
            surface = draw_text(lines[idx], font)
            screen.blit(surface, surface.get_rect(centery=HEIGHT_MIDDLE - dh))

        # render annotated lines on top
        # this includes the middle line so its annotations gradually go from transparent to opaque
        i = idx
        while i >= 0:
            y = HEIGHT_MIDDLE + (i - idx) * TEXT_ROW_HEIGHT - dh
            if y < -TEXT_ROW_HEIGHT // 2:
                break
            if i < len(lines):
                surface = draw_annotated_text(lines[i], font)
                surface.set_alpha(
                    int(255 * dh / TEXT_ROW_HEIGHT)
                    if i == idx
                    else 255 - (idx - i - 1) * 70
                )
                screen.blit(
                    surface,
                    surface.get_rect(centery=y),
                )
            i -= 1

        # render unannotated text on bottom
        i = idx + 1
        while i < len(lines):
            y = HEIGHT_MIDDLE + (i - idx) * TEXT_ROW_HEIGHT - dh
            if y > HEIGHT + TEXT_ROW_HEIGHT // 2:
                break
            surface = draw_text(lines[i], font)
            surface.set_alpha(255 - (i - idx) * 70)
            screen.blit(
                surface,
                surface.get_rect(centery=y),
            )
            i += 1

        # add to running totals
        if idx > last_idx and idx < len(lines):
            last_idx = idx
            _, r1 = spans_part_1(lines[idx])
            result1 += int(r1)
            _, r2 = spans_part_2(lines[idx])
            result2 += int(r2)

        # render running totals
        result1_text = font.render(str(result1), 1, SILVER)
        screen.blit(result1_text, result1_text.get_rect(bottom=HEIGHT - 10, left=10))
        result2_text = font.render(str(result2), 1, GOLD)
        screen.blit(
            result2_text, result2_text.get_rect(bottom=HEIGHT - 10, right=WIDTH - 10)
        )

        # scroll down
        if (
            idx < len(lines) and time.perf_counter() - t0 > 2
        ):  # the delay is so I can launch obs recording =D
            h += scroll_speed
            scroll_speed = min(1 + idx // 10, 50)

        # actually update the screen now
        pg.display.flip()

    pg.quit()
    sys.exit(0)


if __name__ == "__main__":
    run()
