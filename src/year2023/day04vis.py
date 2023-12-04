# Problem statement: https://adventofcode.com/2023/day/4

import sys
import pygame as pg
from aocd import get_data
import time
from dataclasses import dataclass

SILVER = (153, 153, 204)
GOLD = (230, 230, 94)
TEXT_COLOR = (204, 204, 204)
BACKGROUND = (15, 15, 35)
BACKGROUND_2 = (25, 25, 55)

WIDTH = 1280
HEIGHT = 720
QUEUE_HEIGHT = 80
TOTALS_FONT_SIZE = 40

FPS = 60
INITIAL_DELAY = 2
TIME_PER_TURN = 1


@dataclass
class WinNumber:
    n: int
    in_card: bool


@dataclass
class HaveNumber:
    n: int
    match: bool


@dataclass
class Card:
    id: int
    win: list[WinNumber]
    have: list[HaveNumber]
    copies: int = 1
    matches: int = 0
    score: int = 0
    part1_total: int = 0
    part2_total: int = 0


def annotate(text_input):
    annotated_lines = []
    copies_history = []
    lines = text_input.split("\n")
    part1_total = 0
    part2_total = 0
    copies = [1] * len(lines)
    for i, line in enumerate(lines):
        copies_history.append(list(copies))
        card, nums = line.split(": ")
        card_id = int(card.split()[1])
        win, have = nums.split(" | ")
        win = [int(x) for x in win.split()]
        have = [int(x) for x in have.split()]
        win, have = (
            [WinNumber(n, n in have) for n in win],
            [HaveNumber(n, n in win) for n in have],
        )
        matches = sum(h.match for h in have)
        score = 0 if matches == 0 else 2 ** (matches - 1)
        for k in range(matches):
            copies[i + k + 1] += copies[i]
        annotated_lines.append(
            Card(
                card_id, win, have, copies[i], matches, score, part1_total, part2_total
            )
        )
        part1_total += score
        part2_total += copies[i]
    copies_history.append(list(copies))
    return annotated_lines, copies_history


# turn stages end at:
FLY_IN = 0.25 * TIME_PER_TURN  # card flies in from queue, queue moves up
MATCH = 0.5 * TIME_PER_TURN  # matches are highlighted
SYMBOLS = (
    0.75 * TIME_PER_TURN
)  # silver symbols fly to part 1 score, gold symbols fly to queue cards, card flies to part 2 score
SCORES_UPDATE = 1.0 * TIME_PER_TURN  # scores update


def draw_card_raw(card: Card):
    W = 600
    H = 300
    surface = pg.Surface((W, H))
    surface.fill(BACKGROUND_2)
    pg.draw.rect(surface, TEXT_COLOR, pg.Rect(0, 0, W, H), 1, 10)
    pg.draw.line(surface, TEXT_COLOR, (W // 3, 0), (W // 3, H), 1)
    H0 = H // 2
    W0win = W // 6
    font = pg.font.SysFont("monospace", 30)
    symbol = font.render(".", 1, TEXT_COLOR)
    symbol_rect = symbol.get_rect()
    SW, SH = symbol_rect.width, symbol_rect.height
    for i, num in enumerate(card.win):
        t = font.render(str(num.n), 1, TEXT_COLOR)
        right = W0win + 3 * SW + (i % 2 - 1) * 4 * SW
        top = H0 - 2.5 * SH + SH * (i // 2)
        surface.blit(t, t.get_rect(right=right, top=top))
    W0have = W * 2 // 3
    for i, num in enumerate(card.have):
        t = font.render(str(num.n), 1, TEXT_COLOR)
        right = W0have + 9 * SW + (i % 5 - 4) * 4 * SW
        top = H0 - 2.5 * SH + SH * (i // 5)
        surface.blit(t, t.get_rect(right=right, top=top))
    return surface


def draw_card_annotated(card: Card):
    W = 600
    H = 300
    surface = pg.Surface((W, H))
    surface.fill(BACKGROUND_2)
    pg.draw.rect(surface, TEXT_COLOR, pg.Rect(0, 0, W, H), 1, 10)
    pg.draw.line(surface, TEXT_COLOR, (W // 3, 0), (W // 3, H), 1)
    H0 = H // 2
    W0win = W // 6
    font = pg.font.SysFont("monospace", 30)
    symbol = font.render(".", 1, TEXT_COLOR)
    symbol_rect = symbol.get_rect()
    SW, SH = symbol_rect.width, symbol_rect.height
    for i, num in enumerate(card.win):
        color = GOLD if num.in_card else TEXT_COLOR
        t = font.render(str(num.n), 1, color)
        if not num.in_card:
            t.set_alpha(64)
        right = W0win + 3 * SW + (i % 2 - 1) * 4 * SW
        top = H0 - 2.5 * SH + SH * (i // 2)
        surface.blit(t, t.get_rect(right=right, top=top))
    W0have = W * 2 // 3
    for i, num in enumerate(card.have):
        color = GOLD if num.match else TEXT_COLOR
        t = font.render(str(num.n), 1, color)
        if not num.match:
            t.set_alpha(64)
        right = W0have + 9 * SW + (i % 5 - 4) * 4 * SW
        top = H0 - 2.5 * SH + SH * (i // 5)
        surface.blit(t, t.get_rect(right=right, top=top))
    return surface


def card_symbol_locs(card: Card):
    W = 600
    H = 300
    H0 = H // 2
    W0have = W * 2 // 3
    symbol_locations = []
    font = pg.font.SysFont("monospace", 30)
    symbol = font.render(".", 1, TEXT_COLOR)
    symbol_rect = symbol.get_rect()
    SW, SH = symbol_rect.width, symbol_rect.height
    for i, num in enumerate(card.have):
        if num.match:
            right = W0have + 9 * SW + (i % 5 - 4) * 4 * SW
            top = H0 - 2.5 * SH + SH * (i // 5)
            symbol_locations.append((right - SW, top + SH // 2))
    return symbol_locations


def draw_card_id(card: Card):
    W = 600
    H = 300
    surface = pg.Surface((W, H))
    surface.fill(BACKGROUND_2)
    pg.draw.rect(surface, TEXT_COLOR, pg.Rect(0, 0, W, H), 1, 10)

    font = pg.font.SysFont("monospace", 120)
    text = font.render(str(card.id), 1, TEXT_COLOR)
    text_rect = text.get_rect(centerx=W // 2, centery=H // 2)
    surface.blit(text, text_rect)
    return surface


def draw_queue(cards, copies, degree_moved):
    W = WIDTH
    H = QUEUE_HEIGHT
    card_centers = []
    surface = pg.Surface((W, H))
    surface.fill(BACKGROUND)
    if len(cards) == 0:
        return surface, card_centers
    left = 10
    copies_font = pg.font.SysFont("monospace", 14)
    # skip some left space for the first card that is flying away
    skip_w = 0
    card_surf = draw_card_id(cards[0])
    card_surf = pg.transform.smoothscale_by(card_surf, 0.2)
    skip_w += card_surf.get_rect().width
    if copies[0] > 1:
        text = copies_font.render(f" x{copies[0]}", 1, TEXT_COLOR)
        skip_w += text.get_rect().width
    skip_w += 10
    left += int(skip_w * (1 - degree_moved))
    rect = card_surf.get_rect(left=left, centery=H // 2)
    for card, cop in zip(cards[1:], copies[1:]):
        card_surf = draw_card_id(card)
        card_surf = pg.transform.smoothscale_by(
            card_surf, 60 / card_surf.get_rect().height
        )
        rect = card_surf.get_rect(left=left, centery=H // 2)
        card_centers.append(rect.center)
        surface.blit(card_surf, rect)
        left += rect.width
        if cop > 1:
            text = copies_font.render(f" x{cop}", 1, TEXT_COLOR)
            rect = text.get_rect(left=left, centery=H // 2)
            surface.blit(text, rect)
            left += rect.width
        left += 10
        if left > W:
            break
    return surface, card_centers


def run():
    # Get sizes from input data
    text_input = get_data(year=2023, day=4)
    cards, copies_history = annotate(text_input)

    pg.init()
    screen = pg.display.set_mode([WIDTH, HEIGHT])
    pg.display.set_caption("Advent of Code 2023 - Day 4 - Scratchcards")

    card_font = pg.font.SysFont("monospace", 30)
    symbol = card_font.render(".", 1, TEXT_COLOR)
    symbol_rect = symbol.get_rect()
    SW, SH = symbol_rect.width, symbol_rect.height
    gold_symbol = pg.Surface((SW, SW))
    pg.draw.circle(gold_symbol, GOLD, (SW // 2, SW // 2), SW // 2)
    totals_font = pg.font.SysFont("monospace", TOTALS_FONT_SIZE)
    gain_font = pg.font.SysFont("monospace", TOTALS_FONT_SIZE // 2)
    total_1_label = totals_font.render("Part 1: ", 1, SILVER)
    total_1_label_rect = total_1_label.get_rect(
        centery=(HEIGHT - QUEUE_HEIGHT) // 3, left=700
    )
    total_2_label = totals_font.render("Part 2: ", 1, GOLD)
    total_2_label_rect = total_2_label.get_rect(
        centery=(HEIGHT - QUEUE_HEIGHT) * 2 // 3, left=700
    )
    copies_font = pg.font.SysFont("monospace", 14)

    clock = pg.time.Clock()

    t0 = time.perf_counter()
    running = True

    while running:
        clock.tick(FPS)

        t = time.perf_counter() - t0
        current_turn = min(len(cards), int(max(0, t - INITIAL_DELAY) / TIME_PER_TURN))
        dt = max(0, t - INITIAL_DELAY - current_turn * TIME_PER_TURN)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                t0 = time.perf_counter()

        # erase everything
        screen.fill(BACKGROUND)

        # end state - just show totals
        if current_turn == len(cards):
            # render running totals
            screen.blit(total_1_label, total_1_label_rect)
            total_1_value = totals_font.render(
                str(cards[-1].part1_total + cards[-1].score), 1, SILVER
            )
            total_1_value_rect = total_1_value.get_rect(
                centery=(HEIGHT - QUEUE_HEIGHT) // 3, left=total_1_label_rect.right
            )
            screen.blit(total_1_value, total_1_value_rect)
            screen.blit(total_2_label, total_2_label_rect)
            total_2_value = totals_font.render(
                str(cards[-1].part2_total + cards[-1].copies), 1, GOLD
            )
            total_2_value_rect = total_2_value.get_rect(
                centery=(HEIGHT - QUEUE_HEIGHT) * 2 // 3, left=total_2_label_rect.right
            )
            screen.blit(total_2_value, total_2_value_rect)
            # actually update the screen now
            pg.display.flip()
            continue

        # regular animation stuff while cards last
        # stage 1 - fly in
        if dt < FLY_IN:
            moved_degree = dt / FLY_IN
            # render queue of cards
            queue, _ = draw_queue(
                cards[current_turn:],
                copies_history[current_turn][current_turn:],
                moved_degree,
            )
            screen.blit(queue, queue.get_rect(bottom=HEIGHT, left=0))
            # render the current card flying in
            # draw card_id while small and then numbers when large enough
            if moved_degree < 0.5:
                card_surf = draw_card_id(cards[current_turn])
            else:
                card_surf = draw_card_raw((cards[current_turn]))
            # source point is the first position in queue (card center)
            source_x = 10 + 60
            source_y = HEIGHT - 10 - 30
            # destination point is the center of screen
            destination_x = 10 + 300
            destination_y = (HEIGHT - QUEUE_HEIGHT) // 2
            # actual center should be here
            x = source_x + moved_degree * (destination_x - source_x)
            y = source_y + moved_degree * (destination_y - source_y)
            card_surf = pg.transform.smoothscale_by(card_surf, 0.2 + 0.8 * moved_degree)
            rect = card_surf.get_rect(centerx=x, centery=y)
            screen.blit(card_surf, rect)
            copies = copies_history[current_turn][current_turn]
            if copies > 1:
                text = copies_font.render(f" x{copies}", 1, TEXT_COLOR)
                text_rect = text.get_rect(left=rect.right, centery=rect.centery)
                screen.blit(text, text_rect)
            # render running totals
            screen.blit(total_1_label, total_1_label_rect)
            total_1_value = totals_font.render(
                str(cards[current_turn].part1_total), 1, SILVER
            )
            total_1_value_rect = total_1_value.get_rect(
                centery=(HEIGHT - QUEUE_HEIGHT) // 3, left=total_1_label_rect.right
            )
            screen.blit(total_1_value, total_1_value_rect)
            screen.blit(total_2_label, total_2_label_rect)
            total_2_value = totals_font.render(
                str(cards[current_turn].part2_total), 1, GOLD
            )
            total_2_value_rect = total_2_value.get_rect(
                centery=(HEIGHT - QUEUE_HEIGHT) * 2 // 3, left=total_2_label_rect.right
            )
            screen.blit(total_2_value, total_2_value_rect)

        # stage 2 - highlight matches
        elif dt < MATCH:
            # render queue of cards
            queue, _ = draw_queue(
                cards[current_turn:],
                copies_history[current_turn][current_turn:],
                1,
            )
            screen.blit(queue, queue.get_rect(bottom=HEIGHT, left=0))

            # render current card
            degree = int((dt - FLY_IN) * 255 / (MATCH - FLY_IN))
            card_surf = draw_card_raw(cards[current_turn])
            rect = card_surf.get_rect(left=10, centery=(HEIGHT - QUEUE_HEIGHT) // 2)
            card_surf.set_alpha(255 - degree)
            screen.blit(card_surf, rect)
            card_surf = draw_card_annotated(cards[current_turn])
            card_surf.set_alpha(degree)
            screen.blit(card_surf, rect)
            copies = copies_history[current_turn][current_turn]
            if copies > 1:
                text = copies_font.render(f" x{copies}", 1, TEXT_COLOR)
                text_rect = text.get_rect(left=rect.right, centery=rect.centery)
                screen.blit(text, text_rect)

            # render running totals
            screen.blit(total_1_label, total_1_label_rect)
            total_1_value = totals_font.render(
                str(cards[current_turn].part1_total), 1, SILVER
            )
            total_1_value_rect = total_1_value.get_rect(
                centery=(HEIGHT - QUEUE_HEIGHT) // 3, left=total_1_label_rect.right
            )
            screen.blit(total_1_value, total_1_value_rect)
            screen.blit(total_2_label, total_2_label_rect)
            total_2_value = totals_font.render(
                str(cards[current_turn].part2_total), 1, GOLD
            )
            total_2_value_rect = total_2_value.get_rect(
                centery=(HEIGHT - QUEUE_HEIGHT) * 2 // 3, left=total_2_label_rect.right
            )
            screen.blit(total_2_value, total_2_value_rect)

        # stage 3 - fly symbols
        elif dt < SYMBOLS:
            degree_moved = (dt - MATCH) / (SYMBOLS - MATCH)
            # render queue of cards
            queue, card_centers = draw_queue(
                cards[current_turn:],
                copies_history[current_turn][current_turn:],
                1,
            )
            screen.blit(queue, queue.get_rect(bottom=HEIGHT, left=0))

            # render current card
            card_surf = draw_card_annotated(cards[current_turn])
            rect = card_surf.get_rect(left=10, centery=(HEIGHT - QUEUE_HEIGHT) // 2)
            screen.blit(card_surf, rect)
            copies = copies_history[current_turn][current_turn]
            if copies > 1:
                text = copies_font.render(f" x{copies}", 1, TEXT_COLOR)
                text_rect = text.get_rect(left=rect.right, centery=rect.centery)
                screen.blit(text, text_rect)

            # render running totals
            screen.blit(total_1_label, total_1_label_rect)
            total_1_value = totals_font.render(
                str(cards[current_turn].part1_total), 1, SILVER
            )
            total_1_value_rect = total_1_value.get_rect(
                centery=(HEIGHT - QUEUE_HEIGHT) // 3, left=total_1_label_rect.right
            )
            screen.blit(total_1_value, total_1_value_rect)
            total_1_gain = gain_font.render(
                "+" + str(cards[current_turn].score), 1, SILVER
            )
            total_1_gain_rect = total_1_gain.get_rect(
                centery=(HEIGHT - QUEUE_HEIGHT) // 3, left=total_1_value_rect.right
            )
            screen.blit(total_1_gain, total_1_gain_rect)

            screen.blit(total_2_label, total_2_label_rect)
            total_2_value = totals_font.render(
                str(cards[current_turn].part2_total), 1, GOLD
            )
            total_2_value_rect = total_2_value.get_rect(
                centery=(HEIGHT - QUEUE_HEIGHT) * 2 // 3, left=total_2_label_rect.right
            )
            screen.blit(total_2_value, total_2_value_rect)
            total_2_gain = gain_font.render(
                "+" + str(cards[current_turn].copies), 1, GOLD
            )
            total_2_gain_rect = total_2_gain.get_rect(
                centery=(HEIGHT - QUEUE_HEIGHT) * 2 // 3, left=total_2_value_rect.right
            )
            screen.blit(total_2_gain, total_2_gain_rect)

            # render symbols
            symbol_locations = card_symbol_locs(cards[current_turn])
            start_points = [
                (rect.left + x, rect.top + y) for (x, y) in symbol_locations
            ]
            gold_points = []
            for i, (x, y) in enumerate(start_points):
                if i < len(card_centers):
                    x0, y0 = card_centers[i]
                    y0 = HEIGHT - y0
                    gold_points.append((x0, y0))
                else:
                    x0, y0 = card_centers[-1]
                    x0 += 130 * (i + 1 - len(card_centers))
                    y0 = HEIGHT - y0
                    gold_points.append((x0, y0))
            for (x0, y0), (x1, y1) in zip(start_points, gold_points):
                x = x0 + (x1 - x0) * degree_moved
                y = y0 + (y1 - y0) * degree_moved
                screen.blit(
                    gold_symbol,
                    pg.Rect(x - SW // 4, y - SW // 4, SW // 2, SW // 2),
                )
                # pg.draw.circle(screen, GOLD, (x, y), SW // 2)
            silver_points = []
            x0 = total_1_label_rect.left + 10
            y0 = total_1_label_rect.bottom + TOTALS_FONT_SIZE // 2
            for i, (x, y) in enumerate(start_points):
                silver_points.append((x0 + i * 2 * SW, y0))
            for (x0, y0), (x1, y1) in zip(start_points, silver_points):
                x = x0 + (x1 - x0) * degree_moved
                y = y0 + (y1 - y0) * degree_moved
                pg.draw.circle(screen, SILVER, (x, y), SW // 2)

        # stage 4 - update scores
        elif dt < SCORES_UPDATE:
            degree_moved = (dt - SYMBOLS) / (SCORES_UPDATE - SYMBOLS)
            # render queue of cards
            queue, _ = draw_queue(
                cards[current_turn:],
                copies_history[current_turn + 1][current_turn:],
                1,
            )
            screen.blit(queue, queue.get_rect(bottom=HEIGHT, left=0))

            # render current card
            card_surf = draw_card_annotated(cards[current_turn])
            rect = card_surf.get_rect(left=10, centery=(HEIGHT - QUEUE_HEIGHT) // 2)
            screen.blit(card_surf, rect)
            copies = copies_history[current_turn][current_turn]
            if copies > 1:
                text = copies_font.render(f" x{copies}", 1, TEXT_COLOR)
                text_rect = text.get_rect(left=rect.right, centery=rect.centery)
                screen.blit(text, text_rect)

            # render running totals
            screen.blit(total_1_label, total_1_label_rect)
            total_1_value = totals_font.render(
                str(cards[current_turn].part1_total), 1, SILVER
            )
            total_1_value_rect = total_1_value.get_rect(
                centery=(HEIGHT - QUEUE_HEIGHT) // 3, left=total_1_label_rect.right
            )
            screen.blit(total_1_value, total_1_value_rect)
            total_1_gain = gain_font.render(
                "+" + str(cards[current_turn].score), 1, SILVER
            )
            total_1_gain_rect = total_1_gain.get_rect(
                centery=(HEIGHT - QUEUE_HEIGHT) // 3, left=total_1_value_rect.right
            )
            screen.blit(total_1_gain, total_1_gain_rect)

            screen.blit(total_2_label, total_2_label_rect)
            total_2_value = totals_font.render(
                str(cards[current_turn].part2_total), 1, GOLD
            )
            total_2_value_rect = total_2_value.get_rect(
                centery=(HEIGHT - QUEUE_HEIGHT) * 2 // 3, left=total_2_label_rect.right
            )
            screen.blit(total_2_value, total_2_value_rect)
            total_2_gain = gain_font.render(
                "+" + str(cards[current_turn].copies), 1, GOLD
            )
            total_2_gain_rect = total_2_gain.get_rect(
                centery=(HEIGHT - QUEUE_HEIGHT) * 2 // 3, left=total_2_value_rect.right
            )
            screen.blit(total_2_gain, total_2_gain_rect)

            # render silver symbols
            x0 = total_1_label_rect.left + 10
            y0 = total_1_label_rect.bottom + TOTALS_FONT_SIZE // 2
            for i in range(cards[current_turn].matches):
                pg.draw.circle(screen, SILVER, (x0 + i * 2 * SW, y0), SW // 2)

        # actually update the screen now
        pg.display.flip()

    pg.quit()
    sys.exit()


if __name__ == "__main__":
    run()
