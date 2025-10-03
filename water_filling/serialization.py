"""Helper functions for getting data in and out of strings."""

import functools

import numpy as np


@functools.lru_cache(maxsize=1024)
def parse_volume(s):
    try:
        if "." in s:
            arr = np.fromstring(s, sep=",", dtype=np.float64)
        else:
            arr = np.fromstring(s, sep=",", dtype=np.int_)
        if not arr.size == 1:
            raise ValueError
        res = arr[0]
        if not (0 <= res < np.inf):
            raise ValueError
        return res
    except ValueError:
        return None


@functools.lru_cache(maxsize=1024)
def parse_heights(s):
    try:
        res = np.fromstring(s, sep=",")
        if not res.ndim == 1:
            raise ValueError
        if not 0 < res.size < 2**16:
            raise ValueError
        if not np.isfinite(res).all():
            raise ValueError
        return res
    except ValueError:
        return None


def maybe_int(x):
    """If `x` appears to be integer, return it as an integer."""
    rounded = x.round().astype(np.int_)
    if np.allclose(x, rounded):
        return rounded
    return x


def englishify(list_of_numbers):  # anglicize?
    """Convert a list of numbers to a running-text representation.

    For example, `[1, 2, 3]` becomes the string `"1, 2, and 3"`.
    """
    arr = np.asarray(list_of_numbers)
    arr = maybe_int(arr)
    match arr.size:
        case 0:
            raise ValueError("Empty list")
        case 1:
            return str(arr[0])
        case 2:
            return f"{arr[0]} and {arr[1]}"
        case _:
            return ", ".join(str(x) for x in arr[:-1]) + f", and {arr[-1]}"
