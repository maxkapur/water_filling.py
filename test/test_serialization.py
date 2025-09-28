import numpy as np
import pytest

from water_filling import serialization


@pytest.mark.parametrize(
    "s,volume",
    [
        ("0.0", 0.0),
        ("-0.0", 0.0),
        ("1.5", 1.5),
        ("1.500", 1.5),
        ("3", 3.0),
    ],
)
def test_parse_volume(s, volume):
    parsed = serialization.parse_volume(s)
    assert isinstance(parsed, np.float64)
    assert volume == parsed


@pytest.mark.parametrize(
    "s",
    [
        "",
        "asdf",
        "nan",
        "inf",
        "-1",
        "-1.0",
        "1,2,3",
    ],
)
def test_parse_volume__bad(s):
    assert serialization.parse_volume(s) is None


@pytest.mark.parametrize(
    "s,heights",
    [
        ("-1,2,-3,4", [-1, 2, -3, 4]),
        ("-1.0,2.5,-3.0,4.0", [-1, 2.5, -3, 4]),
        ("-1,2,-3,4,", [-1, 2, -3, 4]),
        ("-1, 2, -3.0, 4", [-1, 2, -3, 4]),
        ("-1,2,-3,4", [-1, 2, -3, 4]),
        ("3", [3]),
        ("3,", [3]),
        ("3," * 2**4, [3] * 2**4),
    ],
)
def test_parse_heights(s, heights):
    parsed = serialization.parse_heights(s)
    assert isinstance(parsed[0], np.float64)
    assert np.all(heights == parsed)


@pytest.mark.parametrize(
    "s",
    [
        "",
        "asdf",
        "nan,",
        "inf",
        "3," * 2**16,
    ],
)
def test_parse_heights__bad(s):
    assert serialization.parse_heights(s) is None
