# Problem statement: https://adventofcode.com/2023/day/17

from util.inputs import movechars_dr_dc
import math

from year2023.day17 import search, CrucibleCity, example_input

from matplotlib import pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle
from aocd import get_data


def path_to_xydata(path, y0, x0):
    x, y = x0, y0
    xx, yy = [x], [y]
    for char in path:
        dy, dx = movechars_dr_dc[char]
        x += dx
        y += dy
        xx.append(x)
        yy.append(y)
    return dict(xdata=xx, ydata=yy)


def run():
    # text_input = example_input
    text_input = get_data(year=2023, day=17)
    fig, (ax1, ax2) = plt.subplots(
        nrows=1, ncols=2, figsize=(16, 9), facecolor="#0f0f23", dpi=80
    )
    font = dict(family="monospace", size=20)
    ax1.set_title("Part 1", color="#8a8aba", **font)
    ax2.set_title("Part 2", color="#f0f062", **font)
    ax1.axis("off")
    ax2.axis("off")

    city_1 = CrucibleCity(text_input, 1, 3)
    city_2 = CrucibleCity(text_input, 4, 10)

    ax1.imshow(city_1.costs, interpolation="none", cmap="gray", aspect="auto")
    ax2.imshow(city_1.costs, interpolation="none", cmap="gray", aspect="auto")
    h1 = [[math.nan] * len(city_1.costs[0]) for _ in city_1.costs]
    h2 = [[math.nan] * len(city_1.costs[0]) for _ in city_1.costs]
    im1 = ax1.imshow(h1, cmap="viridis", vmin=0, vmax=1000)
    im2 = ax2.imshow(h2, cmap="viridis", vmin=0, vmax=1000)
    ax1.add_patch(
        Circle(
            (city_1.start[0], city_1.start[1]),
            radius=0.3,
            facecolor="C1",
            lw=1,
        )
    )
    ax1.add_patch(
        Circle(
            (city_1.finish[0], city_1.finish[1]),
            radius=0.3,
            facecolor="C1",
            lw=1,
        )
    )
    ax2.add_patch(
        Circle(
            (city_2.start[0], city_2.start[1]),
            radius=0.3,
            facecolor="C1",
            lw=1,
        )
    )
    ax2.add_patch(
        Circle(
            (city_2.finish[0], city_2.finish[1]),
            radius=0.3,
            facecolor="C1",
            lw=1,
        )
    )
    (trail1,) = ax1.plot([], [], "-", lw=2, color="C1")
    (trail2,) = ax2.plot([], [], "-", lw=2, color="C1")
    search1 = search(city_1, yield_search_states=True)
    search2 = search(city_2, yield_search_states=True)
    steps1 = 0
    steps2 = 0
    done1, done2 = False, False

    def animate(i):
        nonlocal search1, search2, h1, h2, steps1, steps2, done1, done2
        bestcost1, bestcost2 = 0, 0
        state1, state2 = None, None
        data1, data2 = None, None
        if i == 0:
            search1 = search(city_1, yield_search_states=True)
            trail1.set(xdata=[], ydata=[])
            search2 = search(city_2, yield_search_states=True)
            trail2.set(xdata=[], ydata=[])
        elif i > 30:
            if not done1:
                iterations_per_frame = max(1, math.ceil(steps1 * 0.01))
                for _ in range(iterations_per_frame):
                    steps1 += 1
                    try:
                        elem1 = next(search1)
                    except StopIteration:
                        done1 = True
                        break
                    state1, priority, bestcost1, len_queue = elem1
                    x, y = state1.c, state1.r
                    if math.isnan(h1[y][x]) or h1[y][x] > state1.cost:
                        h1[y][x] = state1.cost
                ax1.set_title(
                    f"Part 1: Best cost = {bestcost1}",
                    color="#8a8aba",
                    **font,
                )
                data1 = path_to_xydata(state1.path, *city_1.start)
                im1.set_array(h1)
                trail1.set(**data1)
            if not done2:
                iterations_per_frame = max(1, math.ceil(steps2 * 0.01))
                for _ in range(iterations_per_frame):
                    steps2 += 1
                    try:
                        elem2 = next(search2)
                        state2, priority, bestcost2, len_queue = elem2
                        x, y = state2.c, state2.r
                        if math.isnan(h2[y][x]) or h2[y][x] > state2.cost:
                            h2[y][x] = state2.cost
                    except StopIteration:
                        done2 = True
                        break
                ax2.set_title(
                    f"Part 2: Best cost = {bestcost2}",
                    color="#f0f062",
                    **font,
                )
                im2.set_array(h2)
                data2 = path_to_xydata(state2.path, *city_2.start)
                trail2.set(**data2)

        return (trail1, trail2, im1, im2)

    fig.tight_layout()

    ani = animation.FuncAnimation(
        fig,
        animate,
        interval=50,
        blit=False,
        # frames=24 * 27,
        # repeat_delay=3000,
    )

    # writer = animation.FFMpegWriter(fps=24, metadata=dict(artist="me"), bitrate=1800)
    # ani.save("day_17.mp4", writer=writer)

    plt.show()
