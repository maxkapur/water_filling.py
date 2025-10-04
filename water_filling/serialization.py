"""Helper functions for getting data in and out of strings."""

import functools
from urllib.parse import quote

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
        if "." in s:
            res = np.fromstring(s, sep=",", dtype=np.float64)
        else:
            res = np.fromstring(s, sep=",", dtype=np.int_)
        if not res.ndim == 1:
            raise ValueError
        if not 0 < res.size < 2**16:
            raise ValueError
        if not np.isfinite(res).all():
            raise ValueError
        return res
    except ValueError:
        return None


def to_str(vec_or_scalar):
    """Convert numbers to a string representation.

    Preserves dtypes and serializes for inclusion in the URL parameters.
    """
    arr = np.asanyarray(vec_or_scalar)
    if arr.ndim == 0:
        return str(arr.item())
    return ",".join(str(x) for x in arr)


def to_path(heights_str, volume_str):
    """Escape stringified heights and volumes and compose a URL permalink."""
    return f"/level?heights={quote(heights_str)}&volume={quote(volume_str)}"


def maybe_int(x):
    """If `x` appears to be integer, return it as an integer."""
    rounded = x.round().astype(np.int_)
    if np.allclose(x, rounded):
        return rounded
    return x


def to_english(vec_or_scalar):
    """Convert numbers to a running-text representation.

    For example, `[1, 2, 3]` becomes the string `"1, 2, and 3"`. In contrast to
    `to_str()`, this method is for human readability in English. This method is
    used to reflect a user's input parameters back to them, so it shows the full
    precision available.
    """
    arr = np.asanyarray(vec_or_scalar)
    match arr.size:
        case 0:
            raise ValueError("Empty list")
        case 1:
            return str(arr.item())
        case 2:
            return f"{arr[0]} and {arr[1]}"
        case _:
            return ", ".join(str(x) for x in arr[:-1]) + f", and {arr[-1]}"
