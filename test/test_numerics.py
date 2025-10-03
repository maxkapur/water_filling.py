import numpy as np
import pytest

from water_filling import numerics


def test_volume(triple):
    """`water_filling.volume()` correctly recovers volume."""
    assert np.isclose(numerics.volume(triple.heights, triple.level), triple.volume)


@pytest.mark.parametrize(
    "heights,level",
    [
        ([1, 2, 3, 4], 0.5),
        ([1, 2, 3, 4], -999.0),
        ([-1, 2, -3, -4], -4.5),
        ([-1, 2, -3, -4], -np.inf),  # fine
    ],
)
def test_volume__level_below_min(heights, level):
    """When `level < heights.min()`, test that `volume` clips to 0.0.

    These out-of-bounds cases are excluded from the `triple` fixture because
    the `level` is not unique.
    """
    assert 0.0 == numerics.volume(heights, level)


def test_level(triple):
    """`water_filling.level()` correctly recovers level."""
    level_estimated = numerics.level(triple.heights, triple.volume)
    volume_achieved = numerics.volume(triple.heights, level_estimated)
    assert np.isclose(volume_achieved, triple.volume)
    assert np.isclose(level_estimated, triple.level)


def test_random(triple):
    """`water_filling.random()` returns valid-looking input."""
    heights, volume = numerics.random()
    assert heights.ndim == 1
    assert np.isfinite(heights).all()
    assert volume > 0
