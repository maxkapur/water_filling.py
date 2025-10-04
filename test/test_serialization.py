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
        ("3.0", 3.0),
    ],
)
def test_parse_volume__float(s, volume):
    parsed = serialization.parse_volume(s)
    assert isinstance(parsed, np.float64)
    assert volume == parsed


@pytest.mark.parametrize(
    "s,volume",
    [
        ("0", 0),
        ("-0", 0),
        ("1", 1),
        ("1500", 1500),
        ("3", 3),
    ],
)
def test_parse_volume__int(s, volume):
    parsed = serialization.parse_volume(s)
    assert isinstance(parsed, np.int_)
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
        ("-1,2.0,-3,4", [-1, 2, -3, 4]),
        ("-1.0,2.5,-3.0,4.0", [-1, 2.5, -3, 4]),
        ("-1,2,-3,4.,", [-1, 2, -3, 4]),
        ("-1.0, 2, -3.0, 4", [-1, 2, -3, 4]),
        ("-1,2.,-3,4", [-1, 2, -3, 4]),
        ("3.0", [3]),
        ("3.0,", [3]),
        ("3.0," * 2**4, [3] * 2**4),
    ],
)
def test_parse_heights__float(s, heights):
    parsed = serialization.parse_heights(s)
    assert isinstance(parsed[0], np.float64)
    assert np.all(heights == parsed)


@pytest.mark.parametrize(
    "s,heights",
    [
        ("-1,2,-3,4", [-1, 2, -3, 4]),
        ("-1,2,-3,4,", [-1, 2, -3, 4]),
        ("-1, 2, -3  , 4", [-1, 2, -3, 4]),
        ("-1,2,-3,4", [-1, 2, -3, 4]),
        ("3", [3]),
        ("3,", [3]),
        ("3," * 2**4, [3] * 2**4),
    ],
)
def test_parse_heights__int(s, heights):
    parsed = serialization.parse_heights(s)
    assert isinstance(parsed[0], np.int_)
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


@pytest.mark.parametrize(
    "x,result",
    [
        (np.float64(1.0), 1),
        (np.float64(-1.0), -1),
        (np.float64(-0.0), 0),
    ],
)
def test_maybe_int__scalar_becomes_int(x, result):
    after = serialization.maybe_int(x)
    assert isinstance(after, np.int_)
    assert after == result


@pytest.mark.parametrize(
    "x,result",
    [
        (np.array([1.0, 3.0]), [1, 3]),
        (np.array([-1.0, 3.0]), [-1, 3]),
        (np.array([-0.0, 3.0]), [0, 3]),
    ],
)
def test_maybe_int__array_becomes_int(x, result):
    after = serialization.maybe_int(x)
    assert isinstance(after[0], np.int_)
    assert np.all(after == result)


@pytest.mark.parametrize(
    "x",
    [
        np.float64(3.5),
        np.array([1, 2, 3.5, 4]),
    ],
)
def test_maybe_int__no_change(x):
    assert serialization.maybe_int(x) is x


@pytest.mark.parametrize(
    "vec,s",
    [
        ([0], "0"),
        ([0.0], "0.0"),
        ([0.1], "0.1"),
        ([0, 4], "0,4"),
        ([0, 4.0], "0.0,4.0"),
        ([0, 4.5], "0.0,4.5"),
        ([0, -9, 4], "0,-9,4"),
        ([0, -9, 4.0], "0.0,-9.0,4.0"),
        ([0, -9, 4.5], "0.0,-9.0,4.5"),
    ],
)
def test_to_str__vec(vec, s):
    assert s == serialization.to_str(vec)


@pytest.mark.parametrize(
    "scalar,s",
    [
        (0, "0"),
        (0.0, "0.0"),
        (-0, "0"),
        (-0.0, "-0.0"),
        (1.4, "1.4"),
        (4.0, "4.0"),
        (-4, "-4"),
        (-4.0, "-4.0"),
    ],
)
def test_to_str__scalar(scalar, s):
    assert s == serialization.to_str(scalar)


@pytest.mark.parametrize(
    "vec,s",
    [
        ([0], "0"),
        ([0.0], "0.0"),
        ([0.1], "0.1"),
        ([0, 4], "0 and 4"),
        ([0, 4.0], "0.0 and 4.0"),
        ([0, 4.5], "0.0 and 4.5"),
        ([0, -9, 4], "0, -9, and 4"),
        ([0, -9, 4.0], "0.0, -9.0, and 4.0"),
        ([0, -9, 4.5], "0.0, -9.0, and 4.5"),
    ],
)
def test_to_english__vec(vec, s):
    assert s == serialization.to_english(vec)


# TODO: Use minus sign instead of -


@pytest.mark.parametrize(
    "scalar,s",
    [
        (0, "0"),
        (0.0, "0.0"),
        (-0, "0"),
        (-0.0, "-0.0"),  # Fine
        (1.4, "1.4"),
        (4.0, "4.0"),
        (-4, "-4"),
        (-4.0, "-4.0"),
    ],
)
def test_to_english__scalar(scalar, s):
    assert s == serialization.to_english(scalar)
