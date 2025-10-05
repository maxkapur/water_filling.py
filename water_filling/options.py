"""Command-line options."""

import warnings
from argparse import ArgumentParser
from functools import cache


@cache
def get_options():
    parser = ArgumentParser()

    parser.add_argument(
        "--prefix",
        default="",
        help='Prefix if site is to be hosted on a subdirectory. For example, if prefix="/prefix", then the /random endpoint is available at /prefix/random instead',
    )

    res = parser.parse_args()
    if res.prefix.endswith("/"):
        warnings.warn("--prefix should probably not end with a slash")

    return res
