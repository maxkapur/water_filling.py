"""Microdot frontend."""

from pathlib import Path
from urllib.parse import quote

import mistune
from microdot import Microdot, redirect, send_file
from microdot.jinja import Template

from . import water_filling
from .database import get_level_as_dict_from_parsed
from .serialization import englishify, maybe_int, parse_heights, parse_volume

static_path = Path(__file__).parent / "static"
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
    heights = parse_heights(request.args.get("heights"))
    volume = parse_volume(request.args.get("volume"))
    if heights is None or volume is None:
        return "Bad request", 400

    accept = request.headers.get("Accept", "").lower()
    as_dict = get_level_as_dict_from_parsed(heights, volume)

    if "text/html" in accept:
        return Template("visualize.html").render(
            heights_str=englishify(heights),
            volume_str=str(maybe_int(volume)),
            level_str="%.2f" % as_dict["level"],
            svg_data=as_dict["svg"],
            cached=as_dict["cached"],
        ), {"Content-Type": "text/html"}

    if "image/svg" in accept:
        return as_dict["svg"], {"Content-Type": "image/svg"}

    # Default to JSON
    return as_dict


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
    if parse_heights(heights_str) is None:
        errors.append("Invalid heights input")
    if parse_volume(volume_str) is None:
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
