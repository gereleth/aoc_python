# Problem statement: https://adventofcode.com/2024/day/23

from py5 import Sketch  # , Py5Font
from aocd import data
from .day23 import day_title
from statemachine import StateMachine, State
from functools import cache
import networkx as nx
import py5
from collections import defaultdict

WIDTH = 1920
HEIGHT = 1080
PADDING = 36

SILVER = (153, 153, 204)
GOLD = (230, 230, 94)
TEXT_COLOR = (204, 204, 204)
BACKGROUND = (15, 15, 35)
BACKGROUND_2 = (25, 25, 55)
WHITE = (255, 255, 255)
WALL_COLOR = (200, 200, 200)
FONT_SIZE = 20

text = data  # aocd magic, gets correct input by inspecting filepath for year/day
lines = text.split("\n")
graph = nx.Graph(line.split("-") for line in lines)
maxclique, _ = nx.max_weight_clique(graph, weight=None)
circles = [set(maxclique)]
todo = set(graph.nodes).difference(maxclique)
done = set(maxclique)
while todo:
    nextcircle = set()
    for node in circles[-1]:
        nextcircle.update(graph.neighbors(node))
    nextcircle.difference_update(done)
    todo.difference_update(nextcircle)
    done.update(nextcircle)
    circles.append(set(nextcircle))

circles[0] = ["kc", "og", *(n for n in circles[0] if n not in ("kc", "og"))]
corder = {}
for i, circle in enumerate(circles):
    if i == 0:
        for n, node in enumerate(circle):
            corder[node] = n
        continue
    for node in circle:
        prev = set(graph.neighbors(node)).intersection(circles[i - 1])
        corder[node] = sum(corder[p] for p in prev) / len(prev)

anc = defaultdict(set)
for node in circles[2]:
    par = set(graph.neighbors(node)) & circles[1]
    nb = set(graph.neighbors(node)) & circles[2]
    anc[par.pop()].update(nb)
for par1 in circles[1]:
    for par2 in circles[1]:
        if par1 == par2:
            continue
        print(par1, par2, len(anc[par1] & anc[par2]), len(anc[par1]), len(anc[par2]))


circles = [sorted(c, key=lambda x: corder[x]) for c in circles]


class VisMachine(StateMachine):
    # data fields
    started = True
    ticks = 0
    duration = 0
    done = 1.0
    total_1 = 0
    total_2 = 0
    is_finished = False
    # animation data
    layout = {}
    # animation stages

    init = State(initial=True)
    show_graph = State()
    end = State(final=True)

    transition = init.to(show_graph) | show_graph.to(end)

    def on_enter_show_graph(self):
        R = 100
        for i, circle in enumerate(circles):
            angle = py5.PI * 2 / len(circle)
            for n, node in enumerate(circle):
                self.layout[node] = (
                    WIDTH / 2 + R * py5.cos(angle * n),
                    HEIGHT / 2 - R * py5.sin(angle * n),
                )
            R += 80
        # layout = nx.spectral_layout(graph)
        # for node, xy in layout.items():
        #     x, y = xy
        #     x = WIDTH * (1 + 0.95 * x) / 2
        #     y = HEIGHT * (1 + 0.95 * y) / 2
        #     self.layout[node] = (x, y)

    # timer to change stages
    def tick(self):
        if not self.started:
            return
        self.ticks += 1
        if self.ticks >= self.duration and not self.current_state.final:
            self.ticks = 0
            self.done = 0.0
            self.transition()
        elif self.duration > 0:
            self.done = self.ticks / self.duration


data = VisMachine()


class VisSketch(Sketch):
    def settings(self):
        self.size(WIDTH, HEIGHT)
        self.smooth()

    def setup(self):
        global background
        self.window_title(f"Advent of Code 2024 - Day 21 - {day_title}")
        self.frame_rate(1)

        # prepare and measure font
        font = self.create_font("Liberation Mono", FONT_SIZE)
        self.text_font(font)
        self.text_size(FONT_SIZE)

        self.rect_mode(self.CENTER)
        self.text_align(self.CENTER, self.CENTER)
        data.add_listener(self)

    def mouse_clicked(self):
        # data.started = not data.started
        pass
        self.save_frame(f"d23_image{self.frame_count:03d}.png")

    def draw_nodes(self):
        if len(data.layout) == 0:
            return
        self.stroke(255)
        self.stroke_weight(0.5)
        for a, b in graph.edges:
            if a in circles[0] and b in circles[0]:
                self.stroke(*GOLD)
                self.stroke_weight(2)
            elif a in circles[1] or b in circles[1]:
                self.stroke(255)
                self.stroke_weight(1)
            elif a in circles[2] or b in circles[2]:
                self.stroke(128)
                self.stroke_weight(0.5)
            else:
                continue
                # self.stroke(128)
                # self.stroke_weight(0.5)
            self.line(*data.layout[a], *data.layout[b])
        for node, (x, y) in data.layout.items():
            if node in maxclique:
                self.fill(*GOLD)
            else:
                self.fill(200)
            self.circle(x, y, 40)
            self.fill(0)
            self.text(node, x, y)

    def draw(self):
        data.tick()
        self.background(*BACKGROUND)
        self.draw_nodes()
