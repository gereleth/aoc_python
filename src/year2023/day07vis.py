# Problem statement: https://adventofcode.com/2023/day/7

import sys
import time
from aocd import get_data
import pygame as pg
from collections import Counter
from year2023.day07 import improve_hand_joker, hand_strength, card_rank
from bisect import insort

SILVER = (153, 153, 204)
GOLD = (230, 230, 94)
TEXT_COLOR = (204, 204, 204)
DONE_COLOR = (128, 128, 128)
BACKGROUND = (15, 15, 35, 255)
BACKGROUND_2 = (25, 25, 55)

WIDTH = 1280
HEIGHT = 720
W_PADDING = 50

FPS = 60
INITIAL_DELAY = 2
CARD_TIME = 3
CARD_FONT_SIZE = 30
CARD_WIDTH = int(CARD_FONT_SIZE * 1.1)
CARD_PADDING = int(CARD_FONT_SIZE * 0.1)
CARD_HEIGHT = int(CARD_FONT_SIZE * 1.6)
MARK_RADIUS = 4


def sort_key_silver(item):
    hand, bid = item
    return (hand_strength(hand), *(card_rank[c] for c in hand))


def sort_key_gold(item):
    hand, bid = item
    return (
        hand_strength(improve_hand_joker(hand)),
        *((card_rank[c] if c != "J" else 99) for c in hand),
    )


class CamelCardsGame:
    def __init__(self, text):
        lines = text.split("\n")
        self.hands = []
        for line in lines:
            hand, bid = line.split()
            self.hands.append((hand, int(bid)))
        self.turn = 0
        self.golds = [[] for _ in range(7)]
        self.silvers = [[] for _ in range(7)]

    def update(self, turn):
        while self.turn < min(turn, len(self.hands)):
            hand, bid = self.hands[self.turn]
            silver_strength = hand_strength(hand)
            insort(self.silvers[silver_strength], (hand, bid), key=sort_key_silver)
            gold_strength = hand_strength(improve_hand_joker(hand))
            insort(self.golds[gold_strength], (hand, bid), key=sort_key_gold)
            self.turn += 1


def annotate(hand):
    filled_circles = []
    empty_circles = []
    c = Counter(hand)
    for char, count in c.most_common(5):
        if len(filled_circles) == 0:
            filled_circles.extend([i for i, c in enumerate(hand) if c == char])
        elif count > 1:
            empty_circles.extend([i for i, c in enumerate(hand) if c == char])
            break
        else:
            break
    return filled_circles, empty_circles


def draw_hand_kind(filled, empty, color):
    W = 14 * MARK_RADIUS
    H = W
    surf = pg.Surface((W, H))
    pg.draw.rect(surf, BACKGROUND_2, pg.Rect(0, 0, W, H), 0, 3)
    pg.draw.rect(surf, color, pg.Rect(0, 0, W, H), 1, 3)
    # 0   1 = positions
    #   2
    # 3   4
    positions = [
        (MARK_RADIUS * 3, MARK_RADIUS * 3),
        (MARK_RADIUS * 11, MARK_RADIUS * 3),
        (MARK_RADIUS * 7, MARK_RADIUS * 7),
        (MARK_RADIUS * 3, MARK_RADIUS * 11),
        (MARK_RADIUS * 11, MARK_RADIUS * 11),
    ]
    idx_f = {5: [0, 1, 2, 3, 4], 4: [0, 1, 3, 4], 3: [1, 2, 3], 2: [1, 3], 1: [2]}
    idx_e = {2: [0, 4], 0: []}
    for i in idx_f[filled]:
        pg.draw.circle(surf, color, positions[i], MARK_RADIUS, 0)
    for i in idx_e[empty]:
        pg.draw.circle(surf, color, positions[i], MARK_RADIUS, 1)
    return surf


def draw_hand(hand, font, add_circles=False):
    W = 5 * CARD_WIDTH + 6 * CARD_PADDING
    H = 6 * MARK_RADIUS + CARD_HEIGHT
    surf = pg.Surface((W, H))
    surf.fill(BACKGROUND)

    if add_circles:
        filled_silver, empty_silver = annotate(hand)
        filled_gold, empty_gold = annotate(improve_hand_joker(hand))
    else:
        filled_silver, empty_silver = [], []
        filled_gold, empty_gold = [], []
    for i, card in enumerate(hand):
        left = CARD_PADDING * (i + 1) + CARD_WIDTH * i
        centerx = left + CARD_WIDTH // 2
        rect = pg.Rect(left, 0, CARD_WIDTH, CARD_HEIGHT)
        rect.centery = H // 2
        pg.draw.rect(surf, BACKGROUND_2, rect, 0, 3)
        pg.draw.rect(surf, TEXT_COLOR, rect, 1, 3)
        text = font.render(card, 1, TEXT_COLOR)
        text_rect = text.get_rect(
            centery=H // 2,
            centerx=CARD_PADDING * (i + 1) + CARD_WIDTH * (i + 0.5),
        )
        if i in filled_silver:
            pg.draw.circle(surf, SILVER, (centerx, MARK_RADIUS), MARK_RADIUS, 0)
        if i in empty_silver:
            pg.draw.circle(surf, SILVER, (centerx, MARK_RADIUS), MARK_RADIUS, 1)
        if i in filled_gold:
            pg.draw.circle(surf, GOLD, (centerx, H - MARK_RADIUS), MARK_RADIUS, 0)
        if i in empty_gold:
            pg.draw.circle(surf, GOLD, (centerx, H - MARK_RADIUS), MARK_RADIUS, 1)
        surf.blit(text, text_rect)
    return surf


def run():
    hand_types = [(5, 0), (4, 0), (3, 2), (3, 0), (2, 2), (2, 0), (1, 0)]

    background = pg.Surface((WIDTH, HEIGHT))
    background.fill(BACKGROUND)
    for i, strength in enumerate(hand_types):
        gold = draw_hand_kind(*strength, GOLD)
        rect = gold.get_rect(left=WIDTH // 2 + 200, centery=(i + 0.5) * (HEIGHT / 7))
        background.blit(gold, rect)
        silver = draw_hand_kind(*strength, SILVER)
        rect = silver.get_rect(right=WIDTH // 2 - 200, centery=(i + 0.5) * (HEIGHT / 7))
        background.blit(silver, rect)

    # Get sizes from input data
    text_input = get_data(year=2023, day=7)
    game = CamelCardsGame(text_input)
    N = len(game.hands)

    pg.init()
    screen = pg.display.set_mode([WIDTH, HEIGHT])
    pg.display.set_caption("Advent of Code 2023 - Day 7 - Camel Cards")

    font = pg.font.SysFont("monospace", CARD_FONT_SIZE)
    clock = pg.time.Clock()

    t0 = time.perf_counter()
    last_turn = 0
    last_t = 0
    t1 = t0
    running = True

    duration = 30  # time allowed to scroll all hands
    SPEED = 0.5  # starting speed in hands per second
    max_speed = 2 * N / duration - SPEED  # max speed is speed_factor * speed

    def calc_speed(t):
        if t < 10 or t > duration - 5:
            return SPEED
        else:
            return max_speed

    # main loop
    while running:
        clock.tick(FPS)

        t = max(0, time.perf_counter() - t0 - INITIAL_DELAY)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                t0 = time.perf_counter()
                game = CamelCardsGame(text_input)  # reset game too
                last_turn = 0

        if last_turn < N + 3:
            speed = calc_speed(t)
            turn = last_turn + speed * (t - last_t)
            dt = turn - int(turn)
            last_turn = turn
            last_t = t
            t1 = t

            game.update(int(turn))
            # erase everything
            screen.blit(background, background.get_rect())

            # draw hands
            intturn = int(turn)
            for i in range(-5, 5):
                if intturn + i < 0 or intturn + i > N - 1:
                    continue
                # draw current hand
                hand, bid = game.hands[intturn + i]
                hand_surface = draw_hand(hand, font, add_circles=i == 0)
                hand_rect = hand_surface.get_rect(
                    centerx=WIDTH // 2, centery=HEIGHT // 2 + 50 + 100 * i - 100 * dt
                )
                hand_surface.set_alpha(255 - 60 * abs(i))
                screen.blit(hand_surface, hand_rect)
                if i == 0:
                    strength = hand_strength(hand)
                    pg.draw.aaline(
                        screen,
                        SILVER,
                        (hand_rect.left, hand_rect.centery),
                        (WIDTH // 2 - 200, (strength + 0.5) * HEIGHT / 7),
                    )
                    strength = hand_strength(improve_hand_joker(hand))
                    pg.draw.aaline(
                        screen,
                        GOLD,
                        (hand_rect.right, hand_rect.centery),
                        (WIDTH // 2 + 200, (strength + 0.5) * HEIGHT / 7),
                    )

            # draw gold bids
            x0 = WIDTH // 2 + 300
            for i, golds in enumerate(game.golds):
                y0 = (i + 0.5) * HEIGHT / 7 + 7 * MARK_RADIUS
                for j, (_, bid) in enumerate(golds):
                    pg.draw.line(
                        screen,
                        GOLD,
                        (x0 + j, y0),
                        (x0 + j, y0 - bid * 14 * MARK_RADIUS / 1000),
                    )

            # draw silver bids
            x0 = WIDTH // 2 - 300
            for i, silvers in enumerate(game.silvers):
                y0 = (i + 0.5) * HEIGHT / 7 + 7 * MARK_RADIUS
                for j, (_, bid) in enumerate(silvers):
                    pg.draw.line(
                        screen,
                        SILVER,
                        (x0 - j, y0),
                        (x0 - j, y0 - bid * 14 * MARK_RADIUS / 1000),
                    )

        else:
            # do final counts
            # erase everything
            screen.blit(background, background.get_rect())
            done = min(1, (t - t1) / 10)
            done_idx = int(len(game.hands) * done)
            N = len(game.hands)

            total_gold = 0
            total_silver = 0
            g = 0
            # draw gold bids
            x0 = WIDTH // 2 + 300
            for i, golds in enumerate(game.golds):
                y0 = (i + 0.5) * HEIGHT / 7 + 7 * MARK_RADIUS
                for j, (_, bid) in enumerate(golds):
                    if g <= done_idx:
                        total_gold += (N - g) * bid
                        color = DONE_COLOR
                    else:
                        color = GOLD

                    pg.draw.line(
                        screen,
                        color,
                        (x0 + j, y0),
                        (x0 + j, y0 - bid * 14 * MARK_RADIUS / 1000),
                    )
                    g += 1

            # draw silver bids
            x0 = WIDTH // 2 - 300
            s = 0
            for i, silvers in enumerate(game.silvers):
                y0 = (i + 0.5) * HEIGHT / 7 + 7 * MARK_RADIUS
                for j, (_, bid) in enumerate(silvers):
                    if s <= done_idx:
                        total_silver += (N - s) * bid
                        color = DONE_COLOR
                    else:
                        color = SILVER
                    pg.draw.line(
                        screen,
                        color,
                        (x0 - j, y0),
                        (x0 - j, y0 - bid * 14 * MARK_RADIUS / 1000),
                    )
                    s += 1
            gold_label = font.render("Part 2:", 1, GOLD)
            gold_rect = gold_label.get_rect(
                centerx=WIDTH // 2 + 100, bottom=HEIGHT // 2
            )
            screen.blit(gold_label, gold_rect)
            gold_value = font.render(str(total_gold), 1, GOLD)
            gold_rect = gold_value.get_rect(centerx=WIDTH // 2 + 100, top=HEIGHT // 2)
            screen.blit(gold_value, gold_rect)

            silver_label = font.render("Part 1:", 1, SILVER)
            silver_rect = silver_label.get_rect(
                centerx=WIDTH // 2 - 100, bottom=HEIGHT // 2
            )
            screen.blit(silver_label, silver_rect)
            silver_value = font.render(str(total_silver), 1, SILVER)
            silver_rect = silver_value.get_rect(
                centerx=WIDTH // 2 - 100, top=HEIGHT // 2
            )
            screen.blit(silver_value, silver_rect)
        # actually update the screen now
        pg.display.flip()

    pg.quit()
    sys.exit()


if __name__ == "__main__":
    run()
