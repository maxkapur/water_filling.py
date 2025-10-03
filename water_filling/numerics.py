"""NumPy implementation of linear interpolation method for water-filling."""

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


def level(heights, target_volume):
    """Determine `level` such that `volume(heights, level) = target_volume.`

    Use linear interpolation.
    """
    if not target_volume >= 0.0:
        raise ValueError(volume)

    # Since volume(heights, level) is piecewise linear monotonic in the level,
    # so is its inverse, hence it suffices to construct a vector of `volumes`
    # corresponding to the volume when the level matches each values in
    # `heights`. We could do this in quadratic time using `volume()` above, but
    # here we do it in O(n log n) time by sorting the heights in advance.

    # Interpolation will fail if the level exceeds the highest height; add a
    # dummy height at the end that is guaranteed to be higher than the water
    # level.
    heights = np.sort(heights).astype(np.float64)
    hi = heights[-1] + 1.1 * target_volume / heights.size
    heights = np.append(heights, hi)

    # When level increases from heights[i] to heights[i+1], volume increases by
    # heights[i+1] - heights[i] (the diff) times the number of height elements
    # that are less than heights[i+1] (== i). Hence
    diff = np.diff(heights, prepend=heights[[0]])
    volumes = (diff * np.arange(heights.size)).cumsum()
    # volumes[i] = volume when level is exactly heights[i]

    return np.interp(target_volume, volumes, heights)


def random():
    """Random problem instance `(heights, volume)`."""
    n = rng.integers(10, 21)
    heights = rng.integers(0, 21, size=n)
    volume = rng.integers(1, n * 15)
    return heights, volume
