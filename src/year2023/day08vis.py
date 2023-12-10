# Problem statement: https://adventofcode.com/2023/day/8

import sys
import time
from aocd import get_data
import pygame as pg
from year2023.day08 import parse_input
from math import lcm, pi, sin, cos

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


class WeirdDay8Trajectory:
    """The structure of inputs data IS very specific.
    And this class reflects that. Unusable for anything else.
    """

    def __init__(self, nodes, instructions, start_loc):
        self.nodes = nodes
        self.instructions = instructions
        self.trajectory = []
        self.start_loc = start_loc
        self.end_loc = ""
        self._track_trajectory()
        self.cycle_starts_at = self.trajectory.index(self.end_loc)
        self.period = len(self.trajectory) - self.cycle_starts_at - 1
        self.node_positions = {}
        self._layout_nodes()
        self.turn = 0
        self.discovered_nodes = set()
        self.all_discovered = False

    def _track_trajectory(self):
        self.trajectory = [self.start_loc]
        N = len(self.instructions)
        finish_visits = set()
        steps = 0
        loc = self.start_loc
        while True:
            move_index = steps % N
            move = self.instructions[move_index]
            loc = self.nodes[loc][move]
            self.trajectory.append(loc)
            if loc.endswith("Z"):
                if move_index in finish_visits:
                    # reached end location again at the same move_index
                    # so this cycle will repeat from now on
                    self.end_loc = loc
                    break
                else:
                    finish_visits.add(move_index)
            steps += 1

    def _layout_nodes(self):
        locs = [self.end_loc]
        pos = 0
        circle_pos = {self.end_loc: 0}
        while True:
            next_locs = set(n for loc in locs for n in self.nodes[loc])
            pos += 1
            for n in next_locs:
                circle_pos[n] = pos
            locs = next_locs
            if self.end_loc in locs:
                break
        # handle starting points now
        S = 10
        while self.trajectory[S] not in circle_pos:
            S += 10
        for i in range(S, -1, -1):
            node = self.trajectory[i]
            if node in circle_pos:
                continue
            next_node = self.trajectory[i + 1]
            circle_pos[node] = circle_pos[next_node] - 1
        # put them on a circle
        min_circle_pos = min(circle_pos.values())
        max_circle_pos = max(circle_pos.values())
        n = max_circle_pos - min_circle_pos + 1
        angle = 2 * pi / n
        self.node_positions = {}
        radius_count = {}
        for node, cp in circle_pos.items():
            rc = radius_count.get(cp, 0)
            R = 1 + 0.1 * rc
            radius_count[cp] = rc + 1
            node_angle = pi / 2 - angle * (cp - min_circle_pos)
            self.node_positions[node] = (
                R * cos(node_angle),
                -R * sin(node_angle),
            )

    def get_trajectory_part(self, n=10):
        turn = self.turn
        if turn < self.cycle_starts_at + n:
            return self.trajectory[max(0, turn - n) : turn + 1]
        else:
            return [
                self.trajectory[
                    self.cycle_starts_at + (s - self.cycle_starts_at) % self.period
                ]
                for s in range(turn - n, turn + 1)
            ]

    def update(self, turn):
        if turn < self.turn:
            return
        if not self.all_discovered:
            self.discovered_nodes.update(self.trajectory[self.turn : turn + 1])
            self.all_discovered = len(self.discovered_nodes) == len(self.node_positions)
        self.turn = turn

    def reset(self):
        self.discovered_nodes = set()
        self.all_discovered = False
        self.turn = 0


def get_position(circle_number, circle_position):
    row = circle_number // 3
    col = circle_number % 3
    X = WIDTH // 6 + col * WIDTH // 3
    Y = HEIGHT // 4 + row * HEIGHT // 2
    RY = 0.8 * HEIGHT // 4
    RX = RY
    x0, y0 = circle_position
    return (X + RX * x0, Y + RY * y0)


def run():
    # Get sizes from input data
    text_input = get_data(year=2023, day=8)
    instructions, nodes = parse_input(text_input)
    locations = [loc for loc in nodes.keys() if loc.endswith("A")]
    trajectories = [WeirdDay8Trajectory(nodes, instructions, loc) for loc in locations]
    trajectories.sort(key=lambda tr: tr.cycle_starts_at)

    time_points = [tr.cycle_starts_at for tr in trajectories]
    time_points += [2 * t for t in time_points]
    common_time = trajectories[0].period
    for tr in trajectories[1:]:
        common_time = lcm(common_time, tr.period)
        time_points.append(common_time)
    time_points.sort()

    pg.init()
    screen = pg.display.set_mode([WIDTH, HEIGHT])
    pg.display.set_caption("Advent of Code 2023 - Day 8 - Haunted Wasteland")

    font = pg.font.SysFont("monospace", FONT_SIZE)
    clock = pg.time.Clock()

    t0 = time.perf_counter()
    running = True
    turn = 0
    last_t = 0
    t_2000 = 0
    # main loop
    while running:
        clock.tick(FPS)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                t0 = time.perf_counter()  # reset to start
                last_t = 0
                turn = 0
                t_2000 = 0
                for tr in trajectories:
                    tr.reset()
                continue

        t = max(0, time.perf_counter() - t0 - INITIAL_DELAY)
        dt = t - last_t
        last_t = t

        if turn < 200:
            turn += 10 * dt
        elif turn < 1000:
            turn += min(200, 10 + (t - 20) * 5) * dt
            t_2000 = t
        else:
            index = int((t - t_2000) / 2)
            turn = time_points[min(index, len(time_points) - 1)]
            turn_pct = (t - t_2000) / 2 - index

        screen.fill(BACKGROUND)

        for t, tr in enumerate(trajectories):
            tr.update(int(turn))
            for node, pos in tr.node_positions.items():
                if tr.all_discovered or node in tr.discovered_nodes:
                    spos = get_position(t, pos)
                    for other_node in nodes[node]:
                        if tr.all_discovered or other_node in tr.discovered_nodes:
                            opos = tr.node_positions[other_node]
                            ospos = get_position(t, opos)
                            pg.draw.line(screen, GREY_COLOR, spos, ospos)
                    if node == "ZZZ":
                        color = SILVER
                    elif node.endswith("Z"):
                        color = GOLD
                    elif node.endswith("A"):
                        color = TEXT_COLOR
                    else:
                        color = GREY_COLOR
                    pg.draw.circle(screen, color, spos, 5)
            movement = tr.get_trajectory_part()
            color = SILVER if tr.end_loc == "ZZZ" else GOLD
            # imax = len(movement) - 1
            for i, (a, b) in enumerate(zip(movement[:-1], movement[1:])):
                apos = tr.node_positions[a]
                aspos = get_position(t, apos)
                bpos = tr.node_positions[b]
                bspos = get_position(t, bpos)
                pg.draw.line(screen, color, aspos, bspos, min(i, 5))
            # render z reached at
            messages = []
            if turn >= tr.cycle_starts_at:
                messages.append(f"Z at {tr.cycle_starts_at}")
            if turn >= 2 * tr.cycle_starts_at:
                messages.append(f"Z at {2*tr.cycle_starts_at}")
            if len(messages) == 1:
                text = font.render(
                    messages[0], 1, SILVER if tr.end_loc == "ZZZ" else TEXT_COLOR
                )
                rect = text.get_rect(center=get_position(t, (0, 0)))
                screen.blit(text, rect)
            elif len(messages) == 2:
                text1 = font.render(
                    messages[0], 1, SILVER if tr.end_loc == "ZZZ" else TEXT_COLOR
                )
                text2 = font.render(messages[1], 1, TEXT_COLOR)
                x0, y0 = get_position(t, (0, 0))
                rect1 = text1.get_rect(centerx=x0, bottom=y0)
                rect2 = text2.get_rect(centerx=x0, top=y0)
                screen.blit(text1, rect1)
                screen.blit(text2, rect2)
            if turn > 0 and turn % tr.period == 0:
                pos = get_position(t, tr.node_positions[tr.end_loc])
                pg.draw.circle(
                    screen,
                    SILVER if tr.end_loc == "ZZZ" else GOLD,
                    pos,
                    40 * (1 - turn_pct),
                    1,
                )

        # render current step
        color = TEXT_COLOR if turn < time_points[-1] else GOLD
        text = font.render(f"Time: {int(turn)}", 1, color)
        rect = text.get_rect(top=10, centerx=WIDTH // 3)
        screen.blit(text, rect)
        # actually update the screen now
        pg.display.flip()

    pg.quit()
    sys.exit()


if __name__ == "__main__":
    run()
