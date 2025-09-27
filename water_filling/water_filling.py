import matplotlib.pyplot as plt
import numpy as np

rng = np.random.default_rng()


def volume(heights, level):
    """Volume of water above terrain with given heights.

    For example, `heights = [1, 4, 2, 3]` can be visualized as:

        |
        |   x
        |   x   x
        |   x x x
        | x x x x
         (0 1 2 3)

    When `level = 2.5`, there is a volume of `1.5` units of water above the
    terrain at index `0`, and `0.5` units of water at index `2`, for a total
    volume of `2.0`.
    """
    heights = np.asarray(heights)
    return np.clip(level - heights, 0, np.inf).sum()


def visualize(heights, level):
    """Visualize the water level with a given terrain."""
    water_colors = "teal lightseagreen cornflowerblue tab:cyan".split()
    terrain_colors = "slategray steelblue midnightblue".split()

    heights = np.asarray(heights)
    fig, ax = plt.subplots()
    hmax = np.max([heights.max(), level])
    hmin = heights.min()
    hrange = hmax - hmin
    baseline = hmin - hrange  # Arbitrary value smaller than hmin
    xs = np.linspace(-0.5, heights.size - 0.5, 1000)
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
    ax.set_xlim(xs[0], xs[-1])
    ax.set_ylim(hmin - 0.1 * hrange, hmax + 0.1 * hrange)
    ax.set_xticks([])
    plt.close()
    return fig, ax


def level(heights, target_volume, max_iterations=5000):
    """Determine the level such that `volume(heights, level) = target_volume.`

    Uses the secant method.
    """
    if not target_volume >= 0.0:
        raise ValueError(volume)

    heights = np.asarray(heights)
    lo = heights.min()
    lo_volume = volume(heights, lo)
    hi = heights.max() + target_volume / heights.size
    hi_volume = volume(heights, hi)

    for i in range(max_iterations):
        frac = (target_volume - lo_volume) / (hi_volume - lo_volume)
        mid = lo + frac * (hi - lo)
        mid_volume = volume(heights, mid)
        if np.isclose(mid_volume, target_volume):
            return mid

        if mid_volume > target_volume:
            hi = mid
            hi_volume = mid_volume
        else:
            lo = mid
            lo_volume = mid_volume

    raise RecursionError(i)
