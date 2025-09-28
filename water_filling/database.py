"""Caching logic between the interface and math."""

import io
import sqlite3
from pathlib import Path

import numpy as np

from . import water_filling
from .visualize import visualize

cache_path = Path.home() / ".cache" / "water_filling.cache.db"
cache_path.parent.mkdir(parents=True, exist_ok=True)

con = sqlite3.connect(cache_path)


def get_level_as_dict_from_parsed(heights, volume):
    """Wrapper to compute the level and visualization with a sqlite cache."""
    heights_bytes = heights.tobytes()

    con.execute("""
    CREATE TABLE IF NOT EXISTS water_filling (
        heights BLOB,
        volume REAL,
        level REAL,
        svg TEXT
    ) STRICT
    """)
    if fetched := con.execute(
        "SELECT level, svg FROM water_filling WHERE heights=? AND volume=?",
        (heights_bytes, volume),
    ).fetchone():
        level = np.float64(fetched[0])
        svg_data = fetched[1]
        return {
            "heights": heights.tolist(),
            "volume": volume,
            "level": level,
            "svg": svg_data,
            "cached": True,
        }

    level = water_filling.level(heights, volume)
    fig, ax = visualize(heights, level)
    with io.StringIO() as buf:
        fig.savefig(buf, format="svg", transparent=True, bbox_inches="tight")
        svg_data = buf.getvalue()
    res = {
        "heights": heights.tolist(),
        "volume": volume,
        "level": level,
        "svg": svg_data,
        "cached": False,
    }

    with con:
        con.execute(
            "INSERT INTO water_filling VALUES (?,?,?,?)",
            (heights_bytes, volume, level, svg_data),
        )
    return res
