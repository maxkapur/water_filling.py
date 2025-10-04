"""Caching logic between the interface and math."""

import io
import sqlite3
import time
from pathlib import Path

import matplotlib
import numpy as np

from . import numerics, serialization
from .visualize import visualize

cache_path = Path.home() / ".cache" / "water_filling.cache.db"
cache_path.parent.mkdir(parents=True, exist_ok=True)

con = sqlite3.connect(cache_path)


def fulfill_as_json_serializable_skip_cache(heights, volume):
    """Compute JSON-serializable dict with solution for given problem params.

    Assumes `heights` and `volume` have been parsed as NumPy types (array and
    scalar).

    The returned dictionary can be forwarded to fulfill JSON requests or
    unpacked to populate the `visualize.html` template.
    """
    matplotlib.use("svg")  # Allows starting in non-main thread
    level = numerics.level(heights, volume)
    fig, ax = visualize(heights, level)
    with io.StringIO() as buf:
        fig.savefig(buf, format="svg", transparent=True, bbox_inches="tight")
        svg_data = buf.getvalue()

    return serialization.to_json_serializable_dict(heights, volume, level, svg_data)


def fulfill_as_json_serializable_with_cache(heights, volume):
    """Retrieve JSON-serializable dict with solution for given problem params.

    Wraps `fulfill_as_json_serializable_skip_cache()` with a sqlite3 disk cache.
    """
    assert isinstance(heights, np.ndarray)
    assert isinstance(volume, np.floating) or isinstance(volume, np.integer)
    heights_bytes = heights.tobytes()
    volume_bytes = volume.tobytes()

    con.execute("""
    CREATE TABLE IF NOT EXISTS water_filling (
        heights BLOB,
        volume BLOB,
        level REAL,
        svg TEXT
    ) STRICT
    """)
    if fetched := con.execute(
        "SELECT level, svg FROM water_filling WHERE heights=? AND volume=?",
        (heights_bytes, volume_bytes),
    ).fetchone():
        level = np.float64(fetched[0])
        svg_data = fetched[1]
        as_dict = serialization.to_json_serializable_dict(
            heights, volume, level, svg_data
        )
        as_dict["cached"] = True
        return as_dict

    as_dict = fulfill_as_json_serializable_skip_cache(heights, volume)

    with con:
        con.execute(
            "INSERT INTO water_filling VALUES (?,?,?,?)",
            (heights_bytes, volume_bytes, as_dict["level"], as_dict["svg"]),
        )
    return as_dict
