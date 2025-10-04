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


def to_path(heights_str_or_vec, volume_str_or_scalar):
    """Stringify and escape heights and volumes and compose a URL permalink."""
    if isinstance(heights_str_or_vec, str):
        heights_str = quote(heights_str_or_vec)
    else:
        heights_str = quote(to_str(heights_str_or_vec))

    if isinstance(volume_str_or_scalar, str):
        volume_str = quote(volume_str_or_scalar)
    else:
        volume_str = quote(to_str(volume_str_or_scalar))

    return f"/level?heights={heights_str}&volume={volume_str}"


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


def to_json_serializable_dict(heights, volume, level, svg_data):
    """Format given problem and solution as a JSON-serializable dict."""
    assert isinstance(heights, np.ndarray)
    assert isinstance(volume, np.floating) or isinstance(volume, np.integer)
    # Narrower type because we know this was returned from our function
    assert isinstance(level, np.float64)
    assert isinstance(svg_data, str)

    return {
        "heights": heights.tolist(),
        "volume": volume.item(),
        "level": level,
        "heights_repr": to_english(heights),
        "volume_repr": to_english(volume),
        # Computed value may be a crazy decimal, so truncate it
        "level_repr": "%.2f" % level,
        "svg": svg_data,
        "permalink": to_path(heights, volume),
        # Default values; called will update if needed
        "cached": False,
        "bench": False,
    }


def filtered(response_dict):
    """Filter output of `to_json_serializable_dict()`.

    Leave only the keys that would be useful to a programmatic client.
    """
    return {
        k: v
        for k, v in response_dict.items()
        if k in ["heights", "volume", "level", "svg", "permalink", "cached", "bench"]
    }
