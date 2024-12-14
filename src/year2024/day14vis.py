# Problem statement: https://adventofcode.com/2024/day/14

from py5 import Sketch  # , Py5Font
from aocd import data
from .day14 import day_title, parse_input, calc_new_positions
from statemachine import StateMachine, State
from matplotlib import colormaps
from collections import Counter

# print(Py5Font.list()) # list available fonts
colormap_bright = colormaps.get("viridis")
colormap_gray = colormaps.get("gray")

WIDTH = 1920
HEIGHT = 1080
PADDING = 36

SILVER = (153, 153, 204)
GOLD = (230, 230, 94)
TEXT_COLOR = (204, 204, 204)
BACKGROUND = (15, 15, 35)
BACKGROUND_2 = (25, 25, 55)
WHITE = (255, 255, 255)

FONT_SIZE = 16
LEADING = FONT_SIZE


text = data  # aocd magic, gets correct input by inspecting filepath for year/day
robots = parse_input(data)
R, C = 103, 101


class VisMachine(StateMachine):
    # data fields
    started = False
    ticks = 0
    duration = 0
    done = 1.0
    total_1 = 0
    total_2 = 0
    is_finished = False
    # robot time, not animation time
    time = 0
    next_time = 1
    found_both_anomalies = False
    verified_periods = False
    vertical_start = -1
    horizontal_start = -1
    ultimate_moment = -1
    x_counts = Counter(r[0] for r in robots)
    y_counts = Counter(r[1] for r in robots)
    # animation stages

    init = State(initial=True)

    # look for horizontal and vertical anomalies
    time_passes = State()
    next = init.to(time_passes)

    def on_enter_time_passes(self):
        self.next_time = self.time + 1
        if self.vertical_start < 0 and self.horizontal_start < 0:
            self.duration = 30
        else:
            self.duration = 5

    check_for_anomaly = State()

    def on_enter_check_for_anomaly(self):
        self.time = self.next_time
        pos = calc_new_positions(robots, C, R, self.time)
        self.x_counts = Counter(x for x, y in pos)
        self.y_counts = Counter(y for x, y in pos)
        if max(self.x_counts.values()) > 25:
            if self.vertical_start == -1:
                self.vertical_start = self.time
            self.duration = 120

        elif max(self.y_counts.values()) > 25:
            if self.horizontal_start == -1:
                self.horizontal_start = self.time
            self.duration = 120
        elif self.vertical_start < 0 and self.horizontal_start < 0:
            self.duration = 30
        else:
            self.duration = 0
        self.found_both_anomalies = (
            self.vertical_start > 0
            and self.horizontal_start > 0
            and self.time >= max(self.vertical_start + C, self.horizontal_start + R)
        )
        self.verified_periods = self.time >= max(
            self.vertical_start + 2 * C, self.horizontal_start + 2 * R
        )
        if self.verified_periods:
            for x in range(self.vertical_start, 100000, C):
                double_n = x - self.horizontal_start
                if double_n > 0 and double_n % 2 == 0:
                    n = double_n // 2
                    break
            self.ultimate_moment = self.horizontal_start + n * R

    next |= time_passes.to(check_for_anomaly)

    next |= check_for_anomaly.to(time_passes, unless="found_both_anomalies")

    fast_forward = State()
    next |= check_for_anomaly.to(
        fast_forward, cond="found_both_anomalies and not verified_periods"
    )

    def on_enter_fast_forward(self):
        if self.verified_periods:
            self.next_time = self.ultimate_moment - 1
        elif (self.time - self.vertical_start) % C == 0:
            self.next_time = self.horizontal_start + 2 * R
        elif (self.time - self.horizontal_start) % R == 0:
            self.next_time = self.vertical_start + 2 * C
        self.duration = 60

    next |= fast_forward.to(check_for_anomaly, unless="verified_periods")

    reveal_ultimate_time = State()
    next |= check_for_anomaly.to(reveal_ultimate_time, cond="verified_periods")

    def on_enter_reveal_ultimate_time(self):
        self.x_counts = Counter()
        self.y_counts = Counter()
        self.duration = 120

    reveal_image = State()
    next |= reveal_ultimate_time.to(fast_forward)
    next |= fast_forward.to(reveal_image, cond="verified_periods")

    def on_enter_reveal_image(self):
        self.time = self.next_time
        self.next_time = self.ultimate_moment
        self.duration = 300

    # finish animation
    end = State(final=True)
    next |= reveal_image.to(end)

    def on_enter_end(self):
        self.time = self.ultimate_moment
        pos = calc_new_positions(robots, C, R, self.time)
        self.x_counts = Counter(x for x, y in pos)
        self.y_counts = Counter(y for x, y in pos)

    # timer to change stages
    def tick(self):
        if not self.started:
            return
        self.ticks += 1
        if self.ticks >= self.duration and not self.current_state.final:
            self.ticks = 0
            self.done = 0.0
            self.next()
        elif self.duration > 0:
            self.done = self.ticks / self.duration


data = VisMachine()
R = 103
C = 101
DENSITY_CHART_H = 100
W = min((HEIGHT - 20 - DENSITY_CHART_H) // R, (WIDTH - 20 - DENSITY_CHART_H) // C)
PW = (WIDTH - C * W - DENSITY_CHART_H) // 2
PH = (HEIGHT - R * W - DENSITY_CHART_H) // 2 + DENSITY_CHART_H
NCOLORS = 26
background = None


class VisSketch(Sketch):
    def settings(self):
        self.size(WIDTH, HEIGHT)
        self.smooth()

    def setup(self):
        global background
        self.window_title(f"Advent of Code 2024 - Day 14 - {day_title}")

        # prepare and measure font
        font = self.create_font("Liberation Mono", FONT_SIZE)
        self.text_font(font)
        self.text_leading(LEADING)

        self.rect_mode(self.CENTER)
        self.text_align(self.CENTER, self.CENTER)
        background = self.create_graphics(WIDTH, HEIGHT)
        background.begin_draw()
        background.rect_mode(self.CORNER)
        background.background(*BACKGROUND)
        background.fill(*BACKGROUND_2)
        background.stroke(*TEXT_COLOR)
        background.rect(
            PW - W / 2,
            PH - W / 2,
            C * W,
            R * W,
        )
        background.end_draw()

        data.add_listener(self)

    def mouse_clicked(self):
        data.started = not data.started
        # self.save_frame(f"image{self.frame_count:03d}.png")

    def draw_robots(self, t):
        self.push()
        pos = calc_new_positions(robots, C, R, t)
        self.fill(*TEXT_COLOR)
        self.no_stroke()
        for x, y in pos:
            self.rect(PW + W * x, PH + W * y, W, W)
        self.pop()

    def draw_density_charts(self):
        self.push()
        self.rect_mode(self.CORNER)
        # horizontal density chart
        self.fill(*BACKGROUND_2)
        self.stroke(*TEXT_COLOR)
        self.rect(
            PW - W / 2,
            PH - W / 2 - DENSITY_CHART_H,
            C * W,
            DENSITY_CHART_H,
        )
        self.fill(*TEXT_COLOR, 128)
        self.no_stroke()
        for c in range(C):
            count = data.x_counts[c]
            if count > 0:
                h = count * 3
                self.rect(PW - W / 2 + W * c, PH - W / 2 - h, W, h)
        self.stroke(*TEXT_COLOR, 64)
        self.line(PW - W / 2, PH - W / 2 - 75, PW - W / 2 + W * C, PH - W / 2 - 75)
        if data.vertical_start > 0:
            self.fill(*TEXT_COLOR)
            self.text_align(self.LEFT, self.CENTER)
            times = []
            for t in range(data.vertical_start, data.time + 1, C):
                if len(times) <= 2:
                    times.append(str(t))
                if len(times) == 3:
                    times.append("...")
                    break
            times = ", ".join(times)
            self.text(f"T = {times}", PW - W / 2 + W * C + 10, PH - W / 2 - 75)
        # vertical density chart
        self.fill(*BACKGROUND_2)
        self.stroke(*TEXT_COLOR)
        self.rect(
            PW + W * C - W / 2,
            PH - W / 2,
            DENSITY_CHART_H,
            R * W,
        )
        self.fill(*TEXT_COLOR, 128)
        self.no_stroke()
        for r in range(R):
            count = data.y_counts[r]
            if count > 0:
                h = count * 3
                self.rect(PW + W * C - W / 2, PH - W / 2 + W * r, h, W)
        self.stroke(*TEXT_COLOR, 64)
        self.line(
            PW + W * C - W / 2 + 75,
            PH - W / 2,
            PW + W * C - W / 2 + 75,
            PH - W / 2 + R * W,
        )
        if data.horizontal_start > 0:
            self.fill(*TEXT_COLOR)
            self.text_align(self.LEFT, self.BOTTOM)
            times = []
            for t in range(data.horizontal_start, data.time + 1, R):
                if len(times) <= 2:
                    times.append(str(t))
                if len(times) == 3:
                    times.append("...")
                    break
            times = ", ".join(times)
            self.text(
                f"T = {times}",
                PW + W * C - W / 2 + 75,
                PH - W / 2 - 10,
            )
        self.pop()

    def draw_time(self, t):
        self.push()
        self.fill(*TEXT_COLOR)
        self.text_size(40)
        self.text_align(self.LEFT, self.TOP)
        self.text(
            f"T={t:.1f}s",
            PW + W * C - W / 2 + DENSITY_CHART_H + 20,
            PH - W / 2,
        )
        self.pop()

    def draw_ultimate_time(self):
        if not data.verified_periods:
            return
        if data.current_state == VisMachine.reveal_ultimate_time:
            done = data.done
        elif data.current_state in (
            VisMachine.reveal_image,
            VisMachine.end,
            VisMachine.fast_forward,
        ):
            done = 1.0
        else:
            return
        self.push()
        self.fill(*TEXT_COLOR, int(255 * done))
        self.text_size(30)
        self.text_align(self.RIGHT, self.CENTER)
        self.text(
            f"both at T={data.ultimate_moment}s",
            WIDTH - 20,
            PH - DENSITY_CHART_H / 2,
        )
        self.pop()

    def draw(self):
        data.tick()
        t = data.time
        if data.current_state == VisMachine.time_passes:
            t += data.done
        elif data.current_state == VisMachine.fast_forward:
            t += (
                (data.next_time - data.time)
                * 0.5
                * (1 + self.sin(self.PI * (-0.5 + data.done)))
            )
        elif data.current_state == VisMachine.reveal_image:
            t += (data.ultimate_moment - data.time) * self.sin(
                self.PI * data.done * 0.5
            ) ** 2
        self.image(background, 0, 0)
        self.draw_robots(t)
        self.draw_density_charts()
        self.draw_time(t)
        self.draw_ultimate_time()
        # self.fill(*GOLD)
        # self.text(f"state={data.current_state.id}", 100, 130)
