# Problem statement: https://adventofcode.com/2024/day/16

from py5 import Sketch  # , Py5Font
from aocd import data
from .day16 import day_title, ReindeerMaze, test_input, test_input_2
from statemachine import StateMachine, State
from matplotlib import colormaps
from math import inf

# print(Py5Font.list()) # list available fonts
colormap_bright = colormaps.get("viridis")

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
FONT_SIZE = 30

text = data  # aocd magic, gets correct input by inspecting filepath for year/day


class VisMachine(StateMachine):
    # data fields
    started = False
    ticks = 0
    duration = 0
    done = 1.0
    total_1 = 0
    total_2 = 0
    is_finished = False
    # animation data
    maze = ReindeerMaze(text)
    color_max_cost = 1.2 * maze.get_best_cost()
    search = maze.search(yield_search_states=True)
    state = None
    bestcost = inf
    priority = 0
    queue_length = 0
    tiles_buffer = []
    beststates = []
    iterations_per_step = 1
    besttiles = set()
    # animation stages

    init = State(initial=True)

    step = State()
    transition = init.to(step)
    transition |= step.to.itself(unless="is_finished")

    def on_enter_step(self):
        self.duration = 20
        self.iterations_per_step = min(200, self.iterations_per_step + 1)
        for _ in range(self.iterations_per_step):
            state, priority, bestcost, qlen = next(self.search)
            if isinstance(state, list):
                self.is_finished = True
                self.state = None
                self.beststates = state
                break
            self.tiles_buffer.append((state.r, state.c, state.direction, state.cost))
            self.state = state
            if state.path[-1] == self.maze.finish:
                if state.cost < self.bestcost:
                    self.beststates = [state]
                    self.besttiles = set(state.path)
                elif state.cost == self.bestcost:
                    self.beststates.append(state)
                    self.besttiles.update(state.path)
            self.bestcost = bestcost
            self.priority = priority

    # finish animation
    end = State(final=True)
    transition |= step.to(end, cond="is_finished")

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
R = data.maze.R
C = data.maze.C
W = min((HEIGHT - 20) // R, (WIDTH - 20) // C)
PW = (WIDTH - C * W) // 2
PH = (HEIGHT - R * W) // 2
background = None


class VisSketch(Sketch):
    def settings(self):
        self.size(WIDTH, HEIGHT)
        self.smooth()

    def setup(self):
        global background
        self.window_title(f"Advent of Code 2024 - Day 16 - {day_title}")

        # prepare and measure font
        font = self.create_font("Liberation Mono", FONT_SIZE)
        self.text_font(font)
        self.text_size(FONT_SIZE)

        self.rect_mode(self.CENTER)
        self.text_align(self.CENTER, self.CENTER)
        background = self.create_graphics(WIDTH, HEIGHT)
        background.begin_draw()
        self.draw_walls(gr=background)
        background.end_draw()

        data.add_listener(self)

    def mouse_clicked(self):
        data.started = not data.started
        pass
        # self.save_frame(f"image{self.frame_count:03d}.png")

    def draw_walls(self, gr=None):
        g = self if gr is None else gr
        g.push()
        g.rect_mode(self.CORNER)
        g.background(*BACKGROUND)
        g.fill(*BACKGROUND_2)
        g.stroke(*WALL_COLOR)
        g.rect(PW - W / 2, PH - W / 2, C * W, R * W)
        g.fill(*WALL_COLOR, 32)
        g.rect(PW - W / 2, PH - W / 2, C * W, R * W)
        g.rect_mode(self.CENTER)
        g.fill(*WALL_COLOR, 64)
        g.no_stroke()
        for r, line in enumerate(data.maze.lines):
            for c, char in enumerate(line):
                if char == "#":
                    g.rect(PW + c * W, PH + r * W, W, W)
        g.pop()

    def draw_tiles(self, gr=None):
        g = self if gr is None else gr
        g.push()
        g.rect_mode(self.CENTER)
        g.no_stroke()
        for r, c, direction, cost in data.tiles_buffer:
            color = colormap_bright(0.2 + 0.8 * cost / data.color_max_cost)
            g.fill(*(int(255 * c) for c in color))
            g.rect(PW + c * W, PH + r * W, W, W)
        g.pop()
        data.tiles_buffer.clear()

    def draw_totals(self):
        self.push()
        self.text_align(self.LEFT, self.TOP)
        y0 = PH
        x = PW + W * C + 20
        self.text_size(FONT_SIZE)
        self.fill(*SILVER)
        self.text(
            f"Best cost:\n{'?' if data.bestcost is inf else data.bestcost} >= {data.priority}",
            x,
            y0,
        )
        if len(data.beststates) > 0:
            self.fill(*GOLD)
            self.text(
                f"{len(data.beststates)} routes\n{len(data.besttiles)} tiles",
                x,
                y0 + 4 * FONT_SIZE,
            )
        self.pop()

    def draw_route(self):
        self.push()
        self.shape_mode(self.LINES)
        self.stroke_weight(W / 2)
        self.no_fill()

        if data.state is not None:
            self.stroke(*SILVER)
            self.begin_shape()
            for r, c in data.state.path:
                self.vertex(PW + W * c, PH + W * r)
            self.end_shape()

        self.stroke(*GOLD)
        for state in data.beststates:
            self.begin_shape()
            for r, c in state.path:
                self.vertex(PW + W * c, PH + W * r)
            self.end_shape()
        self.pop()

    def draw(self):
        data.tick()
        self.image(background, 0, 0)
        self.draw_route()
        self.draw_totals()
        if data.tiles_buffer:
            background.begin_draw()
            self.draw_tiles(gr=background)
            background.end_draw()
