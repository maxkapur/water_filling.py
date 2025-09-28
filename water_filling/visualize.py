"""Matplotlib graphical representation of water level."""

import matplotlib.pyplot as plt
import numpy as np

from .water_filling import rng


def visualize(heights, level):
    """Visualize the water level with a given terrain."""
    water_colors = "teal lightseagreen cornflowerblue tab:cyan".split()
    terrain_colors = "slategray steelblue midnightblue".split()

    heights = np.asarray(heights)
    fig, ax = plt.subplots()

    hmax = np.max([heights.max(), level])
    hmin = heights.min()
    if np.isclose(hrange := hmax - hmin, 0.0):
        # Handle singularity when all heights == level
        hmax += 0.5
        hmin -= 0.5
        hrange = hmax - hmin
    baseline = hmin - hrange  # Arbitrary value smaller than hmin
    xs = np.linspace(-0.5, heights.size - 0.5, 1000)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xticks([])
    ax.set_xlim(xs[0], xs[-1])
    ax.set_ylim(hmin - 0.1 * hrange, hmax + 0.1 * hrange)

    ax.fill_between(
        xs,
        level + 0.01 * hrange * np.sin(25 * xs / heights.size),
        y2=baseline,
        hatch=".",
        fc=rng.choice(water_colors),
    )
    ax.bar(
        np.arange(heights.size),
        heights - baseline,
        bottom=baseline,
        width=1.0,
        fc=rng.choice(terrain_colors),
        edgecolor="black",
    )

    plt.close()
    return fig, ax
