"""Helper functions for getting data in and out of strings."""

import functools

import numpy as np


@functools.lru_cache(maxsize=1024)
def volume_parser(s):
    try:
        arr = np.fromstring(s, sep=",")
        if not arr.size == 1:
            raise ValueError
        res = arr[0]
        if not res >= 0:
            raise ValueError
        return res
    except ValueError:
        return None


@functools.lru_cache(maxsize=1024)
def heights_parser(s):
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


def englishify(list_of_numbers):  # anglicize?
    """Convert a list of numbers to a running-text representation.

    For example, `[1, 2, 3]` becomes the string `"1, 2, and 3"`.
    """
    match len(list_of_numbers):
        case 0:
            raise ValueError("Empty list")
        case 1:
            return str(list_of_numbers[0])
        case 2:
            return f"{list_of_numbers[0]} and {list_of_numbers[1]}"
        case _:
            return (
                ", ".join(str(x) for x in list_of_numbers[:-1])
                + f", and {list_of_numbers[-1]}"
            )
