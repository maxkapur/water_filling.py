from collections import namedtuple

import pytest

WaterFillingTriple = namedtuple("WaterFillingTriple", "heights volume level".split())


@pytest.fixture(
    scope="module",
    params=[
        WaterFillingTriple([1, 2, 3, 4], 0.0, 1.0),
        WaterFillingTriple([1, 2, 3, 4], 0.5, 1.5),
        WaterFillingTriple([1, 2, 3, 4], 2.0, 2.5),
        WaterFillingTriple([1, 2, 3, 4], 6.0, 4.0),
        WaterFillingTriple([1, 2, 3, 4], 30.0, 10.0),
        WaterFillingTriple([-1, 2, -3, -4], 0.0, -4.0),
        WaterFillingTriple([-1, 2, -3, -4], 0.5, -3.5),
        WaterFillingTriple([-1, 2, -3, -4], 8.0, 0.0),
        WaterFillingTriple([-1, 2, -3, -4], 12.5, 1.5),
        WaterFillingTriple([-1, 2, -3, -4], 14.0, 2.0),
        WaterFillingTriple([-1, 2, -3, -4], 18.0, 3.0),
    ],
)
def triple(request):
    """Triple of valid `heights`, `volume`, and `level` for water filling."""
    yield request.param
