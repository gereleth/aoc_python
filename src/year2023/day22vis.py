# Problem statement: https://adventofcode.com/2023/day/22

import numpy as np
import math

from year2023.day22 import Brick, parse_brick, example_input_1, fall_down

from matplotlib import pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle
from matplotlib.collections import PolyCollection
from aocd import get_data
from random import uniform


def run():
    text_input = example_input_1
    text_input = get_data(year=2023, day=22)
    font = dict(family="monospace", size=20)
    bricks_up = [parse_brick(line) for line in text_input.split()]
    bricks_up.sort(key=lambda b: b.z0)
    bricks_down = [parse_brick(line) for line in text_input.split()]
    bricks_down.sort(key=lambda b: b.z0)
    bricks_down = fall_down(bricks_down)

    fig = plt.figure(facecolor="#070723", figsize=(16, 9), dpi=80)
    ax = fig.add_subplot(projection="3d", facecolor="#070723")
    ax.axis("off")

    x = [brick.x0 for brick in bricks_up]
    dx = [brick.x1 - brick.x0 + 1 for brick in bricks_up]
    y = [brick.y0 for brick in bricks_up]
    dy = [brick.y1 - brick.y0 + 1 for brick in bricks_up]
    z = [brick.z0 for brick in bricks_up]
    dz = [brick.z1 - brick.z0 + 1 for brick in bricks_up]
    colors = [
        (uniform(0.7, 1), uniform(0.7, 0.99), uniform(0.7, 0.99)) for _ in bricks_up
    ]
    z_down = [brick.z0 for brick in bricks_down]
    zmax = max(z_down)
    bars = ax.bar3d(x, y, z, dx, dy, dz, zsort="average", color=colors)
    ax.set_zlim(0, min(30, max(z) * 1.2))

    ax.set_aspect("equal")
    speed = 0
    distance = 0
    gravity = 0.1

    def animate(i):
        nonlocal bars, speed, distance
        bars.remove()
        speed += gravity * 0.1 * i
        distance += speed * 0.1 * i
        z = [
            brick_down.z0 + max(0, brick_up.z0 - brick_down.z0 - distance)
            for k, (brick_up, brick_down) in enumerate(zip(bricks_up, bricks_down))
        ]
        zmin = max(zz for zz, zd in zip(z, z_down) if zz == zd)
        # print(zmin)
        bars = ax.bar3d(
            x,
            y,
            z,
            dx,
            dy,
            dz,
            zsort="average",
            color=colors,
        )
        # z0, z1 = ax.get_zlim()
        # ax.set_zlim(max(0, zmin + 5 - (z1 - z0)), min(zmax, zmin + 5))

        return (bars,)

    fig.tight_layout()

    ani = animation.FuncAnimation(
        fig,
        animate,
        interval=200,
        blit=False,
        # frames=24 * 27,
        # repeat_delay=3000,
    )

    # writer = animation.FFMpegWriter(fps=24, metadata=dict(artist="me"), bitrate=1800)
    # ani.save("day_17.mp4", writer=writer)

    plt.show()
