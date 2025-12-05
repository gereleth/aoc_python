# Problem statement: https://adventofcode.com/2025/day/4

from matplotlib import pyplot as plt
import matplotlib.animation as animation
import numpy as np

from aocd import data


def run():
    fig, ax = plt.subplots(figsize=(12, 9), facecolor="#08306b")
    ax.axis("off")
    ax.axis("equal")

    lines = data.split()
    paper = np.zeros((len(lines), len(lines[0])), dtype=int)
    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            if char == "@":
                paper[y, x] = 80
    delta = np.zeros_like(paper)

    im = ax.imshow(paper, interpolation="none", cmap="Blues_r", vmin=0, vmax=100)
    fig.tight_layout()
    countdown = 24

    def animate(i):
        nonlocal delta, paper, countdown
        if countdown > 0:
            countdown -= 1
            return
        delta *= 0
        for y, line in enumerate(paper):
            for x, val in enumerate(line):
                if val <= 0:
                    continue
                nearby = 0
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        if (
                            y + dy < 0
                            or y + dy == len(lines)
                            or x + dx < 0
                            or x + dx >= len(line)
                        ):
                            continue
                        if paper[y + dy][x + dx] > 0:
                            nearby += 1
                if nearby <= 4:
                    delta[y, x] = -16
        paper += delta
        # if np.sum(delta) == 0:
        #     im.set_array(cumul)
        # else:
        im.set_array(paper)
        return (im,)

    ani = animation.FuncAnimation(
        fig,
        animate,
        interval=50,
        blit=False,
        frames=24 * 15,
        # repeat_delay=3000,
    )

    # writer = animation.FFMpegWriter(fps=24, metadata=dict(artist="me"), bitrate=1800)
    # ani.save("day_04.mp4", writer=writer)

    plt.show()
