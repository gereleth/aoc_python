# Problem statement: https://adventofcode.com/2023/day/19

import sys
import pygame as pg
from aocd import get_data
import time
from dataclasses import dataclass
from year2023.day19 import (
    parse_input,
    example_input,
    split_parts,
    total_combinations,
    fits,
)
from util.segments import Segment1D

SILVER = (153, 153, 204)
GOLD = (230, 230, 94)
GOLD_2 = (138, 138, 56)
TEXT_COLOR = (204, 204, 204)
BACKGROUND = (15, 15, 35)
BACKGROUND_2 = (25, 25, 55)
TRANSPARENT = (0, 0, 0, 0)

WIDTH = 1280
HEIGHT = 720
PADDING = 20

W_PART = 200
H_PART = 100
W_QUEUE = W_PART + 60 + PADDING

FPS = 60
DOT_RADIUS = 5
LINE_WIDTH = 5


def draw_part(part):
    surface = pg.Surface((W_PART, H_PART))
    surface.fill(BACKGROUND)
    pg.draw.rect(surface, TEXT_COLOR, surface.get_rect(), 1)
    x0 = 20
    x1 = W_PART - 20
    stepy = H_PART // 5
    for i in range(4):
        y = stepy * (i + 1)
        pg.draw.line(surface, TEXT_COLOR, (x0, y), (x1, y), 1)
        key = "xmas"[i]
        segment = part[key]
        if isinstance(segment, int):
            xa = round(x0 + (x1 - x0) * (segment - 1) / 3999)
            pg.draw.circle(surface, TEXT_COLOR, (xa, y), LINE_WIDTH)
        else:
            a, b = segment.a, segment.b
            xa = round(x0 + (x1 - x0) * (a - 1) / (3999))
            xb = round(x0 + (x1 - x0) * (b - 1) / (3999))
            pg.draw.line(surface, TEXT_COLOR, (xa, y), (xb, y), LINE_WIDTH)
    return surface


def draw_workflow_step(step, font, color):
    kind, data, send_to = step
    surface = pg.Surface((W_PART + 60, H_PART)).convert_alpha()
    surface.fill(TRANSPARENT)
    pg.draw.rect(surface, color, pg.Rect(0, 0, W_PART, H_PART), 1)
    pg.draw.rect(surface, color, pg.Rect(W_PART, 0, 60, H_PART), 1)

    x0 = 20
    x1 = W_PART - 20
    stepy = H_PART // 5
    if kind == "check":
        property, comparison, value = data
        y = stepy * ("xmas".index(property) + 1)
        if comparison == "<":
            a = 1
            b = value
        else:
            a = value
            b = 4000
        xa = round(x0 + (x1 - x0) * (a - 1) / (3999))
        xb = round(x0 + (x1 - x0) * (b - 1) / (3999))
        pg.draw.rect(surface, color, pg.Rect(xa, y - stepy // 2, xb - xa, stepy), 1)
        for i in range(4):
            y = stepy * (i + 1)
            pg.draw.line(surface, color, (x0, y), (x1, y), 1)
    dest = font.render(send_to, 1, color)
    surface.blit(dest, dest.get_rect(centery=H_PART // 2, centerx=W_PART + 30))
    return surface


def draw_queue_item(key, part, font, color):
    surface = pg.Surface((W_PART + 60, H_PART))
    surface.fill(BACKGROUND)
    if part is not None:
        ps = draw_part(part)
        surface.blit(ps, ps.get_rect())
    pg.draw.rect(surface, color, pg.Rect(0, 0, W_PART, H_PART), 1)
    pg.draw.rect(surface, color, pg.Rect(W_PART, 0, 60, H_PART))
    dest = font.render(key, 1, BACKGROUND)
    surface.blit(dest, dest.get_rect(centery=H_PART // 2, centerx=W_PART + 30))
    return surface


class QueueItem:
    def __init__(self, part, workflow_key, font, color):
        self.part = part
        self.workflow_key = workflow_key
        self.font = font
        self.color = color
        self.surface = draw_queue_item(workflow_key, part, font, color)

    def remove_part(self):
        part = self.part
        self.part = None
        self.surface = draw_queue_item(self.workflow_key, None, self.font, self.color)
        return part


class AnimState:
    def __init__(self, workflows, parts, font, total_font, top, task):
        self.workflows = workflows
        self.font = font
        self.total_font = total_font
        self.top = top
        self.task = task
        self.color = SILVER if task == 1 else GOLD_2
        self.text_color = SILVER if task == 1 else GOLD
        self.stage = "init"
        self.t = time.perf_counter()
        self.stage_started_at = self.t
        self.stage_done_share = 0
        self.queue = []  # queue of (part + workflow) items
        self.workflow = []  # list of workflow steps
        self.part = None  # current part going through a workflow
        self.step_index = 0  # index of current step in workflow
        self.sent_to_queue = None  # item that is to be added to the queue
        self.total = 0
        workflow_key = "in"
        if task == 1:
            for part in parts:
                queue_item = QueueItem(part, workflow_key, self.font, self.color)
                self.queue.append(queue_item)
        else:
            part = {key: Segment1D(1, 4000) for key in "xmas"}
            queue_item = QueueItem(part, workflow_key, self.font, self.color)
            self.queue.append(queue_item)

    def get_duration(self, stage):
        # maybe define overrides here for some stages
        # returns (action duration, total_duration)
        return {
            "init": (0.5, 0.5),
            "send_away": (0.1, 0.1),
            "accept": (1, 2),
        }.get(stage, (1, 1.2))

    def update(self):
        t = time.perf_counter()
        action_time, total_time = self.get_duration(self.stage)
        self.stage_done_share = min(1, (t - self.stage_started_at) / action_time)
        if t - self.stage_started_at >= total_time:
            self.t = t
            self.next_stage()

    def next_stage(self):
        if self.stage == "init":
            self.stage = "queue"
        elif self.stage == "queue":
            if len(self.queue) == 0:
                self.stage = "finished"
            else:
                self.workflow = self.workflows[self.queue[0].workflow_key]
                self.stage = "show_workflows"
                self.step_index = 0
        elif self.stage == "show_workflows":
            self.stage = "drop_part"
            self.part = self.queue[0].remove_part()
        elif self.stage in ("drop_part", "raise_steps"):
            (kind, data, send_to) = self.workflow[self.step_index]
            if kind == "check":
                if self.task == 1:
                    if fits(self.part, *data):
                        self.sent_to_queue = QueueItem(
                            self.part, send_to, self.font, self.color
                        )
                        self.part = None
                        self.stage = "send_away"
                    else:
                        if self.step_index + 1 < len(self.workflow):
                            self.stage = "raise_steps"
                            self.step_index += 1
                        else:
                            self.queue.pop(0)
                            self.stage = "queue"
                else:
                    yes, no = split_parts(self.part, *data)
                    self.sent_to_queue = QueueItem(yes, send_to, self.font, self.color)
                    self.part = no
                    self.stage = "send_away"
            elif kind == "send":
                self.sent_to_queue = QueueItem(
                    self.part, send_to, self.font, self.color
                )
                self.part = None
                self.stage = "send_away"
        elif self.stage == "send_away":
            if self.sent_to_queue.workflow_key == "A":
                self.stage = "accept"
            elif self.sent_to_queue.workflow_key == "R":
                self.stage = "reject"
            else:
                self.stage = "send_to_queue"
        elif self.stage in ("send_to_queue", "accept", "reject"):
            if self.stage == "send_to_queue":
                self.queue.insert(1, self.sent_to_queue)
            elif self.stage == "accept":
                if self.task == 1:
                    self.total += sum(self.sent_to_queue.part.values())
                else:
                    self.total += total_combinations(self.sent_to_queue.part)
            self.sent_to_queue = None
            if self.task == 2 and self.step_index + 1 < len(self.workflow):
                self.stage = "raise_steps"
                self.step_index += 1
            else:
                self.queue.pop(0)
                self.stage = "queue"
        self.stage_started_at = self.t
        self.update()

    def get_queue_render_data(self):
        left0 = PADDING
        left = PADDING + W_QUEUE
        data = {
            "left0": left0,
            "left": left,
            "items": self.queue,
            "top": self.top + PADDING,
        }
        if self.stage == "init":
            data["left0"] = left
        if self.stage == "queue":
            data["left0"] = left0 + W_QUEUE * (1 - self.stage_done_share)
            data["left"] = data["left0"] + W_QUEUE
        elif self.stage == "send_to_queue":
            data["left"] = PADDING + round(W_QUEUE * (1 + self.stage_done_share))
        return data

    def get_workflows_render_data(self):
        left0 = PADDING
        top0 = self.top + PADDING + H_PART + PADDING
        data = {"left": left0, "top": top0, "items": []}
        if self.stage not in ("queue", "init", "finished"):
            if self.stage == "raise_steps":
                data["top"] = (
                    data["top"]
                    + H_PART
                    + PADDING
                    - self.stage_done_share * (H_PART + PADDING)
                )
            for i, step in enumerate(self.workflow[self.step_index :]):
                if self.stage in ("send_to_queue", "accept", "reject") and i == 0:
                    data["top"] += H_PART + PADDING
                else:
                    surf = draw_workflow_step(step, self.font, self.color)
                    data["items"].append(surf)
        return data

    def get_part_render_data(self):
        left0 = PADDING
        top0 = self.top + PADDING
        data = {"left": left0, "top": top0}
        if self.part is not None:
            data["surface"] = draw_part(self.part)
        if self.stage == "drop_part":
            data["top"] = top0 + round((H_PART + PADDING) * self.stage_done_share)
        else:
            data["top"] = top0 + H_PART + PADDING
        return data

    def get_sent_away_render_data(self):
        if self.stage == "send_to_queue":
            data = {"surface": self.sent_to_queue.surface}
            left0 = PADDING
            top = self.top + PADDING + H_PART + PADDING

            distance = WIDTH - left0 + H_PART + PADDING
            done_distance = self.stage_done_share * distance
            dleft = W_QUEUE
            left = min(left0 + done_distance, left0 + dleft)
            if left - left0 < done_distance:
                top = top - min(H_PART + PADDING, done_distance - (left - left0))
            data["left"] = left
            data["top"] = top
            return data
        elif self.stage == "reject":
            data = {"surface": self.sent_to_queue.surface}
            left0 = PADDING
            top = self.top + PADDING + H_PART + PADDING

            distance = WIDTH - left0 + H_PART + PADDING
            done_distance = self.stage_done_share * distance
            dleft = W_QUEUE * 2
            left = max(left0 - done_distance, left0 - dleft)
            data["left"] = left
            data["top"] = top
            return data
        elif self.stage == "accept":
            data = {"surface": self.sent_to_queue.surface}
            left0 = PADDING
            top = self.top + PADDING + H_PART + PADDING

            distance = WIDTH - left0 + H_PART + PADDING
            done_distance = self.stage_done_share * distance
            dleft = W_QUEUE
            left = min(left0 + done_distance, left0 + dleft)
            data["left"] = left
            data["top"] = top
            if self.task == 1:
                text = " + ".join(str(i) for i in self.sent_to_queue.part.values())
                text += " = " + str(sum(self.sent_to_queue.part.values()))
            else:
                text = " * ".join(
                    str(len(segment)) for segment in self.sent_to_queue.part.values()
                )
                text += " = " + str(total_combinations(self.sent_to_queue.part))
            data["text_label"] = self.font.render("Accepted:", 1, self.text_color)
            data["text"] = self.font.render(text, 1, self.text_color)
            return data
        else:
            return {}

    def render(self, screen):
        # render queue
        data = self.get_queue_render_data()
        top = data["top"]
        items = data["items"]
        for i, item in enumerate(items):
            left = (
                data["left0"] if i == 0 else data["left"] + (i - 1) * (W_PART + 60 + 20)
            )
            surf = item.surface
            rect = surf.get_rect(top=top, left=left)
            screen.blit(surf, rect)
            if left > WIDTH:
                break

        # render part
        data = self.get_part_render_data()
        if "surface" in data:
            surf = data["surface"]
            rect = surf.get_rect(left=data["left"], top=data["top"])
            screen.blit(surf, rect)

        # render workflow steps
        data = self.get_workflows_render_data()
        left = data["left"]
        top = data["top"]
        for surf in data["items"]:
            rect = surf.get_rect(top=top, left=left)
            screen.blit(surf, rect)
            top += rect.height + 20
            if top > HEIGHT:
                break

        # render sent away queue item
        data = self.get_sent_away_render_data()
        if "surface" in data:
            surf = data["surface"]
            rect = surf.get_rect(top=data["top"], left=data["left"])
            screen.blit(surf, rect)
            if "text" in data:
                screen.blit(
                    data["text_label"],
                    data["text_label"].get_rect(
                        left=rect.right + 20, bottom=rect.centery
                    ),
                )
                screen.blit(
                    data["text"],
                    data["text"].get_rect(left=rect.right + 20, top=rect.centery),
                )

        # render total
        text = self.total_font.render(f"Total: {self.total}", 1, self.text_color)
        rect = text.get_rect(
            left=(W_QUEUE * 2 + PADDING),
            top=self.top + 2 * (H_PART + PADDING) + PADDING,
        )
        screen.blit(text, rect)


def run():
    text_input = example_input
    text_input = get_data(year=2023, day=19)

    workflows, parts = parse_input(text_input)
    pg.init()
    screen = pg.display.set_mode([WIDTH, HEIGHT])
    pg.display.set_caption("Advent of Code 2023 - Day 19 - Aplenty")

    font = pg.font.SysFont("monospace", 16)
    total_font = pg.font.SysFont("monospace", 32)
    clock = pg.time.Clock()

    running = True

    silver_state = AnimState(workflows, parts, font, total_font, -PADDING // 2, 1)
    gold_state = AnimState(
        workflows, parts, font, total_font, HEIGHT // 2 - PADDING // 2, 2
    )

    ymid = HEIGHT // 2

    # main loop
    while running:
        clock.tick(FPS)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                t0 = time.perf_counter()

        gold_state.update()
        silver_state.update()

        # erase everything
        screen.fill(BACKGROUND)
        silver_state.render(screen)

        screen.fill(BACKGROUND, pg.Rect(0, ymid, WIDTH, HEIGHT // 2))
        pg.draw.line(screen, BACKGROUND_2, (0, ymid), (WIDTH, ymid), 3)

        gold_state.render(screen)

        # actually update the screen now
        pg.display.flip()

    pg.quit()
    sys.exit()


if __name__ == "__main__":
    run()
