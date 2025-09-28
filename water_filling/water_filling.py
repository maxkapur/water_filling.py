"""NumPy implementation of secant method for the water-filling problem."""

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
