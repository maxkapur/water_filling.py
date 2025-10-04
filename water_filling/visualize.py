"""Matplotlib graphical representation of water level."""

import matplotlib.pyplot as plt
import numpy as np

from water_filling import colors

waveform = "triangle"


def visualize(heights, level):
    """Visualize the water level with a given terrain."""
    heights = np.asanyarray(heights)
    fig, ax = plt.subplots()

    hmax = np.max([heights.max(), level])
    hmin = heights.min()
    if np.isclose(hrange := hmax - hmin, 0.0):
        # Handle singularity when all heights == level
        hmax += 0.5
        hmin -= 0.5
        hrange = hmax - hmin
    baseline = hmin - hrange  # Arbitrary value smaller than hmin

    if waveform == "triangle":
        xs = np.linspace(-0.5, heights.size - 0.5, 12)
        ys = level + 0.01 * hrange * np.power(-1, np.arange(xs.size))
    elif waveform == "sine":
        xs = np.linspace(-0.5, heights.size - 0.5, 1000)
        ys = level + 0.01 * hrange * np.sin(25 * xs / heights.size)
        ys = level + 0.01 * hrange * np.power(-1, np.arange(xs.size))
    elif waveform == "straight":
        xs = np.array([-0.5, heights.size - 0.5])
        ys = np.array([level, level])

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xticks([])
    ax.set_xlim(xs[0], xs[-1])
    ax.set_ylim(hmin - 0.1 * hrange, hmax + 0.1 * hrange)

    ax.fill_between(
        xs,
        ys,
        y2=baseline,
        fc=colors.colors["water"],
        edgecolor=colors.colors["gray"],
    )
    ax.bar(
        np.arange(heights.size),
        heights - baseline,
        bottom=baseline,
        width=1.0,
        hatch="x",
        fc=colors.colors["terrain"],
        edgecolor=colors.colors["gray"],
    )

    plt.close()
    return fig, ax
