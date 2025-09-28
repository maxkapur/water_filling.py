import functools
import io
import sqlite3
from pathlib import Path
from urllib.parse import quote

import mistune
import numpy as np
from microdot import Microdot, redirect
from microdot.jinja import Template

from . import water_filling
from .visualize import visualize

cache_path = Path.home() / ".cache" / "water_filling.cache.db"
cache_path.parent.mkdir(parents=True, exist_ok=True)
con = sqlite3.connect(cache_path)

app = Microdot()
Template.initialize(Path(__file__).parent / "templates")


def populate_globals():
    with open(Path(__file__).parent.parent / "README.md") as markdown_file:
        readme_markdown = markdown_file.read()
    header_markdown, *_ = readme_markdown.split("<!-- end_site_header -->")
    header_markdown = header_markdown.strip()
    Template.jinja_env.globals["header_html"] = mistune.html(header_markdown)


populate_globals()


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


def random_str_input():
    n = water_filling.rng.integers(10, 21)
    heights = water_filling.rng.integers(0, 21, size=n)
    volume = water_filling.rng.integers(1, n * 15)
    heights_str = ",".join(str(x) for x in heights)
    volume_str = str(volume)
    return heights_str, volume_str


@app.get("/level")
async def get_level(request):
    heights = heights_parser(request.args.get("heights"))
    volume = volume_parser(request.args.get("volume"))
    if heights is None or volume is None:
        return "Bad request", 400

    accept = request.headers.get("Accept", "").lower()
    as_dict = get_level_as_dict_from_parsed(heights, volume)

    if "text/html" in accept:
        return Template("visualize.html").render(
            heights_str=englishify(heights),
            volume_str=str(volume),
            level_str="%.2f" % as_dict["level"],
            svg_data=as_dict["svg"],
            cached=as_dict["cached"],
        ), {"Content-Type": "text/html"}

    if "image/svg" in accept:
        return as_dict["svg"], {"Content-Type": "image/svg"}

    # Default to JSON
    return as_dict


def get_level_as_dict_from_parsed(heights, volume):
    """Wrapper to compute the level and visualization with a sqlite cache."""
    heights_bytes = heights.tobytes()
    volume_bytes = volume.tobytes()

    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS water_filling(heights, volume, level, svg)")
    cur.execute(
        "SELECT level, svg FROM water_filling WHERE heights=? AND volume=?",
        (heights_bytes, volume_bytes),
    )
    if fetched := cur.fetchone():
        level = np.frombuffer(fetched[0])[0]
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
        fig.savefig(buf, format="svg")
        svg_data = buf.getvalue()
    res = {
        "heights": heights.tolist(),
        "volume": volume,
        "level": level,
        "svg": svg_data,
        "cached": False,
    }
    cur.execute(
        "INSERT INTO water_filling VALUES (?,?,?,?)",
        (heights.tobytes(), volume.tobytes(), level.tobytes(), svg_data),
    )
    con.commit()
    return res


@app.get("/")
async def get_index(request):
    heights_str, volume_str = random_str_input()
    if errors_str := request.args.get("errors"):
        errors = errors_str.split(";")
    else:
        errors = []
    return Template("form.html").render(
        heights_str=request.args.get("heights") or heights_str,
        volume_str=request.args.get("volume") or volume_str,
        errors=errors,
    ), {"Content-Type": "text/html"}


@app.post("/level")
async def post_level(request):
    heights_str = request.form.get("heights")
    volume_str = request.form.get("volume")

    errors = []
    if heights_parser(heights_str) is None:
        errors.append("Invalid heights input")
    if volume_parser(volume_str) is None:
        errors.append("Invalid volume input")
    if errors:
        error_str = ";".join(errors)
        return redirect(
            f"/?errors={quote(error_str)}&heights={quote(heights_str)}&volume={quote(volume_str)}"
        )

    return redirect(f"/level?heights={quote(heights_str)}&volume={quote(volume_str)}")


@app.get("/random")
async def get_random(request):
    heights_str, volume_str = random_str_input()
    return redirect(f"/level?heights={quote(heights_str)}&volume={quote(volume_str)}")
