# Problem statement: https://adventofcode.com/2024/day/9

from py5 import Sketch  # , Py5Font
from aocd import get_data
from .day09 import day_title, test_input, calculate_checksum
from statemachine import StateMachine, State
from collections import deque, defaultdict
import heapq
from math import ceil, sqrt
from matplotlib import colormaps

# print(Py5Font.list()) # list available fonts
colormap = colormaps.get("plasma")

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


text = get_data(year=2024, day=9, block=True)


def parse_input(text):
    files = deque()
    empty1 = deque()
    empty2 = defaultdict(list)

    file_id = 0
    is_file = True
    index = 0
    for char in text:
        n = int(char)
        if is_file:
            files.append((file_id, index, n))
            file_id += 1
        elif n > 0:
            empty1.append((index, n))
            heapq.heappush(empty2[n], index)
        index += n
        is_file = not is_file
    return files, empty1, empty2


class VisMachine(StateMachine):
    # data fields
    started = False
    ticks = 0
    duration = 0
    done = 1.0
    total_1 = 0
    total_2 = 0
    files1, empty1, empty2 = parse_input(text)
    moved1 = []
    files2 = list(files1)
    out1 = []
    in1 = []
    out2 = []
    in2 = []
    index2 = len(files2)

    done1 = False
    done2 = False

    # animation stages

    init = State(initial=True)

    fragmentation_step = State()

    next = init.to(fragmentation_step)

    next |= fragmentation_step.to.itself(unless="done1 and done2")

    def do_one_file_part_1(self):
        if self.done1:
            return
        (file_id, file_index, file_size) = self.files1.pop()
        self.out1.append((file_id, file_index, file_size))
        while file_size > 0 and len(self.empty1) > 0:
            empty_index, empty_size = self.empty1.popleft()
            if empty_index >= file_index:
                continue
            if empty_size <= file_size:
                self.in1.append((file_id, empty_index, empty_size))
                self.moved1.append((file_id, empty_index, empty_size))
                file_size -= empty_size
            else:
                self.in1.append((file_id, empty_index, file_size))
                self.moved1.append((file_id, empty_index, file_size))
                self.empty1.appendleft(
                    (empty_index + file_size, empty_size - file_size)
                )
                file_size = 0
        if file_size > 0:
            # could not move whole file, add back a leftover
            self.files1.append((file_id, file_index, file_size))
            self.in1.append((file_id, file_index, file_size))
        if len(self.empty1) == 0:
            self.done1 = True

    def do_one_file_part_2(self):
        if self.done2:
            return
        self.index2 -= 1
        if self.index2 < 0:
            self.done2 = True
            return
        (file_id, file_index, file_size) = self.files2[self.index2]

        empty_index, empty_size = min(
            (
                (positions[0], size)
                for size, positions in self.empty2.items()
                if len(positions) > 0 and (size >= file_size)
            ),
            default=(0, 0),
        )
        if empty_size == 0 or file_index < empty_index:
            # either nowhere to put this file at all
            # or would have to move it to the right
            return
        # put file at the empty space
        self.in2.append((file_id, empty_index, file_size))
        self.out2.append((file_id, file_index, file_size))
        self.files2[self.index2] = (file_id, empty_index, file_size)
        # remove this empty space from heap
        heapq.heappop(self.empty2[empty_size])
        # possibly add a new leftover empty space
        new_empty_size = empty_size - file_size
        if new_empty_size > 0:
            new_empty_index = empty_index + file_size
            heapq.heappush(self.empty2[new_empty_size], new_empty_index)

    def on_enter_fragmentation_step(self):
        for _ in range(10):
            self.do_one_file_part_1()
            self.do_one_file_part_2()

    # finish animation
    end = State(final=True)

    next |= fragmentation_step.to(end, cond="done1 and done2")

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
N = sum(f[-1] for f in data.files1) + sum(f[-1] for f in data.empty1)
R = ceil(sqrt(N) * 2 * HEIGHT / WIDTH)
C = ceil(sqrt(N) * WIDTH * 0.5 / HEIGHT)
print(R, C, R * C, N)
W = min(HEIGHT // R, WIDTH * 0.5 // C)
print(W)
PW = (WIDTH // 2 - C * W) // 2
PH = (HEIGHT - R * W) // 2
NCOLORS = len(data.files1)
background = None


class VisSketch(Sketch):
    def settings(self):
        self.size(WIDTH, HEIGHT)
        self.smooth()

    def setup(self):
        self.window_title(f"Advent of Code 2024 - Day 9 - {day_title}")

        # prepare and measure font
        font = self.create_font("Liberation Mono", FONT_SIZE)
        self.text_font(font)
        self.text_leading(LEADING)

        self.rect_mode(self.CENTER)
        self.text_align(self.CENTER, self.CENTER)
        self.background(*BACKGROUND)

        self.fill(*BACKGROUND_2)
        self.stroke(*SILVER)
        self.rect(PW + W * (C / 2 - 1), PH + W * (R / 2 - 1), (C + 5) * W, (R + 5) * W)

        self.fill(*BACKGROUND_2)
        self.stroke(*GOLD)
        self.rect(
            PW + WIDTH // 2 + W * (C / 2 - 1),
            PH + W * (R / 2 - 1),
            (C + 5) * W,
            (R + 5) * W,
        )

        self.stroke(*BACKGROUND_2)
        for file in data.files1:
            self.draw_one_file(*file, part=1)
            self.draw_one_file(*file, part=2)

        data.add_listener(self)

    def mouse_clicked(self):
        if data.started:
            title = "-".join(s.lower() for s in day_title.split())
            self.save_frame(f"outputs/2024-day09-{title}-{self.frame_count}.png")
        data.started = not data.started

    def draw_one_file(self, file_id, index, size, part=1, erase=False):
        if not erase:
            self.stroke(*BACKGROUND_2)
            r, g, b, _ = colormap(self.constrain(file_id / NCOLORS, 0.5, 1.0))
            self.fill(int(255 * r), int(255 * g), int(255 * b))
        else:
            self.fill(*BACKGROUND_2)
            self.stroke(*BACKGROUND_2)
        x0 = PW if part == 1 else PW + WIDTH // 2
        for i in range(size):
            y = PH + W * ((index + i) // C)
            x = x0 + W * ((index + i) % C)
            self.rect(x, y, W, W)

    def draw(self):
        data.tick()

        for file in data.out1:
            self.draw_one_file(*file, part=1, erase=True)
        data.out1.clear()
        for file in data.in1:
            self.draw_one_file(*file, part=1, erase=False)
        data.in1.clear()
        for file in data.out2:
            self.draw_one_file(*file, part=2, erase=True)
        data.out2.clear()
        for file in data.in2:
            self.draw_one_file(*file, part=2, erase=False)
        data.in2.clear()
