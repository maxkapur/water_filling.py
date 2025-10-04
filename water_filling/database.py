"""Caching logic between the interface and math."""

import io
import sqlite3
from pathlib import Path

import numpy as np

from . import numerics, serialization
from .visualize import visualize

cache_path = Path.home() / ".cache" / "water_filling.cache.db"
cache_path.parent.mkdir(parents=True, exist_ok=True)

con = sqlite3.connect(cache_path)


def get_level_as_dict_from_parsed(heights, volume):
    """Wrapper to compute the level and visualization with a sqlite cache.

    Assume `heights` and `volume` have been parsed as NumPy types (array and
    scalar)."""
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
        return {
            "heights": heights.tolist(),
            "volume": volume,
            "level": level,
            "heights_repr": serialization.to_english(heights),
            "volume_repr": serialization.to_english(volume),
            # Computed value may be a crazy decimal, so truncate it
            "level_repr": "%.2f" % level,
            "svg": svg_data,
            "cached": True,
        }

    level = numerics.level(heights, volume)
    fig, ax = visualize(heights, level)
    with io.StringIO() as buf:
        fig.savefig(buf, format="svg", transparent=True, bbox_inches="tight")
        svg_data = buf.getvalue()
    res = {
        "heights": heights.tolist(),
        "volume": volume,
        "level": level,
        "heights_repr": serialization.to_english(heights),
        "volume_repr": serialization.to_english(volume),
        # Computed value may be a crazy decimal, so truncate it
        "level_repr": "%.2f" % level,
        "svg": svg_data,
        "cached": False,
    }

    with con:
        con.execute(
            "INSERT INTO water_filling VALUES (?,?,?,?)",
            (heights_bytes, volume_bytes, level, svg_data),
        )
    return res
