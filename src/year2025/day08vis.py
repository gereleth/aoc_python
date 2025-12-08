# Problem statement: https://adventofcode.com/2025/day/8

from py5 import Sketch, PI
from aocd import data
import numpy as np
from statemachine import StateMachine, State
from .day08 import day_title, test_input, get_sorted_pairs

import numpy as np
from io import StringIO

# print(Py5Font.list()) # list available fonts

WIDTH = 1920
HEIGHT = 1080

SILVER = (153, 153, 204)
GOLD = (230, 230, 94)
TEXT_COLOR = (204, 204, 204)
BACKGROUND = (15, 15, 35)
BACKGROUND_2 = (25, 25, 55)
WHITE = (255, 255, 255)


boxes = np.loadtxt(StringIO(data), delimiter=",", dtype=np.float64)
boxes = boxes * 1000 / boxes.max()
lines = []
pairs = get_sorted_pairs(boxes)
connections = {i: {i} for i in range(len(boxes))}
done = False
t0 = 0


class VisSketch(Sketch):
    def settings(self):
        self.size(WIDTH, HEIGHT, self.P3D)
        self.smooth()

    def setup(self):
        self.window_title(f"Advent of Code 2025 - Day 8 - {day_title}")

    def mouse_clicked(self):
        global t0
        t0 = self.millis()

    def draw_lines(self):
        if len(lines) == 0:
            return
        self.push()
        self.stroke(*TEXT_COLOR, 160)
        self.stroke_weight(3)
        self.lines(lines[:-1])
        if done:
            self.stroke(*GOLD)
        else:
            self.stroke(*TEXT_COLOR)
        self.line(*lines[-1])
        self.pop()

    def draw_points(self):
        self.push()
        self.stroke(*GOLD)
        self.stroke_weight(10)
        self.points(boxes)
        self.pop()

    def draw(self):
        global done
        self.background(*BACKGROUND)
        self.fill(*BACKGROUND_2, 0)
        m = 0
        if t0 > 0:
            t = self.millis() - t0
            m = PI * t / 5000
            i = t // 5
            while not done and i > len(lines):
                a, b = next(pairs)
                lines.append((*boxes[a, :], *boxes[b, :]))
                conn = connections[a]
                conn.update(connections[b])
                if len(conn) == len(boxes):
                    done = True
                for box in conn:
                    connections[box] = conn
        # (500,500,500) is the center of the points cloud
        # camera flies around and always looks at the center
        self.camera(
            500 + 1500 * self.cos(m),
            500 + 1500 * self.sin(m),
            500,  # camera position
            500,
            500,
            500,  # camera looks at this point
            0,
            0,
            1,  # this means the Z axis is up
        )
        self.draw_lines()
        self.draw_points()
