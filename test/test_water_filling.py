import numpy as np
import pytest

import water_filling


@pytest.mark.parametrize(
    "heights,level,volume",
    [
        ([1, 2, 3, 4], 0.5, 0.0),
        ([1, 2, 3, 4], 1.0, 0.0),
        ([1, 2, 3, 4], 1.5, 0.5),
        ([1, 2, 3, 4], 2.5, 2.0),
        ([1, 2, 3, 4], 4.0, 6.0),
        ([1, 2, 3, 4], 10.0, 30.0),
        ([-1, 2, -3, -4], -4.5, 0.0),
        ([-1, 2, -3, -4], -4.0, 0.0),
        ([-1, 2, -3, -4], -3.5, 0.5),
        ([-1, 2, -3, -4], 0.0, 8.0),
        ([-1, 2, -3, -4], 1.5, 12.5),
        ([-1, 2, -3, -4], 2.0, 14.0),
        ([-1, 2, -3, -4], 3.0, 18.0),
    ],
)
def test_volume(heights, level, volume):
    assert np.isclose(water_filling.volume(heights, level), volume)


@pytest.mark.parametrize(
    "heights,target_volume,level",
    [
        ([1, 2, 3, 4], 0.0, 1.0),  # Non-unique solution
        ([1, 2, 3, 4], 0.5, 1.5),
        ([1, 2, 3, 4], 2.0, 2.5),
        ([1, 2, 3, 4], 6.0, 4.0),
        ([1, 2, 3, 4], 30.0, 10.0),
        ([-1, 2, -3, -4], 0.0, -4.0),  # Non-unique solution
        ([-1, 2, -3, -4], 0.5, -3.5),
        ([-1, 2, -3, -4], 8.0, 0.0),
        ([-1, 2, -3, -4], 12.5, 1.5),
        ([-1, 2, -3, -4], 14.0, 2.0),
        ([-1, 2, -3, -4], 18.0, 3.0),
    ],
)
def test_level(heights, target_volume, level):
    # These simple cases should converge in far fewer iterations
    level_estimated = water_filling.level(heights, target_volume, max_iterations=25)
    volume_achieved = water_filling.volume(heights, level_estimated)
    assert np.isclose(volume_achieved, target_volume)
    # looser tolerance here because the bisection search converges based on
    # level, not volume, not level (which it doesn't know)
    assert np.isclose(level_estimated, level, atol=1e-4)
