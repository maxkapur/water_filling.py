import io
from pathlib import Path
from urllib.parse import quote

import aiosqlite
import mistune
import numpy as np
from microdot import Microdot, redirect, send_file
from microdot.jinja import Template

from . import water_filling
from .serialization import englishify, heights_parser, volume_parser
from .visualize import visualize

static_path = Path(__file__).parent / "static"
cache_path = Path.home() / ".cache" / "water_filling.cache.db"
cache_path.parent.mkdir(parents=True, exist_ok=True)

app = Microdot()
Template.initialize(Path(__file__).parent / "templates")


def populate_globals():
    with open(Path(__file__).parent.parent / "README.md") as markdown_file:
        readme_markdown = markdown_file.read()
    header_markdown, *_ = readme_markdown.split("<!-- end_site_header -->")
    header_markdown = header_markdown.strip()
    Template.jinja_env.globals["header_html"] = mistune.html(header_markdown)


populate_globals()


@app.get("/level")
async def get_level(request):
    heights = heights_parser(request.args.get("heights"))
    volume = volume_parser(request.args.get("volume"))
    if heights is None or volume is None:
        return "Bad request", 400

    accept = request.headers.get("Accept", "").lower()
    as_dict = await get_level_as_dict_from_parsed(heights, volume)

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


async def get_level_as_dict_from_parsed(heights, volume):
    """Wrapper to compute the level and visualization with a sqlite cache."""
    heights_bytes = heights.tobytes()

    async with aiosqlite.connect(cache_path) as con:
        await con.execute("""
        CREATE TABLE IF NOT EXISTS water_filling (
            heights BLOB,
            volume REAL,
            level REAL,
            svg TEXT
        ) STRICT
        """)
        cur = await con.execute(
            "SELECT level, svg FROM water_filling WHERE heights=? AND volume=?",
            (heights_bytes, volume),
        )
        if fetched := await cur.fetchone():
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
        fig.savefig(buf, format="svg")
        svg_data = buf.getvalue()
    res = {
        "heights": heights.tolist(),
        "volume": volume,
        "level": level,
        "svg": svg_data,
        "cached": False,
    }
    async with aiosqlite.connect(cache_path) as con:
        await con.execute(
            "INSERT INTO water_filling VALUES (?,?,?,?)",
            (heights_bytes, volume, level, svg_data),
        )
        await con.commit()
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


@app.route("/static/<path:path>")
async def static(request, path):
    if ".." in path:
        # Disallow directory traversal
        return "Not found", 404
    return send_file(str(static_path / path), max_age=86400)


def random_str_input():
    """Random problem instance, formatted as strings to insert in URL."""
    n = water_filling.rng.integers(10, 21)
    heights = water_filling.rng.integers(0, 21, size=n)
    volume = water_filling.rng.integers(1, n * 15)
    heights_str = ",".join(str(x) for x in heights)
    volume_str = str(volume)
    return heights_str, volume_str
