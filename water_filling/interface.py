"""Microdot frontend."""

from pathlib import Path
from urllib.parse import quote

import jinja2
import mistune
from microdot import Microdot, redirect
from microdot.jinja import Template

from . import colors, serialization
from .database import get_level_as_dict_from_parsed


def initialize_app():
    """Initialize `app` and populate Jinja template globals."""
    app = Microdot()

    Template.initialize(
        Path(__file__).parent / "templates",
        # enable_async=True,
        undefined=jinja2.StrictUndefined,
    )

    with open(Path(__file__).parent.parent / "README.md") as markdown_file:
        readme_markdown = markdown_file.read()
    header_markdown, *_ = readme_markdown.split("<!-- end_site_header -->")
    header_markdown = header_markdown.strip()
    Template.jinja_env.globals["header_html"] = mistune.html(header_markdown)

    Template.jinja_env.globals["colors"] = colors.colors

    return app


app = initialize_app()


@app.get("/level")
async def get_level(request):
    heights = serialization.parse_heights(request.args.get("heights"))
    volume = serialization.parse_volume(request.args.get("volume"))
    if heights is None or volume is None:
        return "Bad request", 400

    accept = request.headers.get("Accept", "").lower()
    as_dict = get_level_as_dict_from_parsed(heights, volume)

    if "text/html" in accept:
        return Template("visualize.html").render(
            heights_str=serialization.englishify(heights),
            volume_str=str(serialization.maybe_int(volume)),
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
    heights_str, volume_str = serialization.random_str_input()
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
    if serialization.parse_heights(heights_str) is None:
        errors.append("Invalid heights input")
    if serialization.parse_volume(volume_str) is None:
        errors.append("Invalid volume input")
    if errors:
        error_str = ";".join(errors)
        return redirect(
            f"/?errors={quote(error_str)}&heights={quote(heights_str)}&volume={quote(volume_str)}"
        )

    return redirect(f"/level?heights={quote(heights_str)}&volume={quote(volume_str)}")


@app.get("/random")
async def get_random(request):
    heights_str, volume_str = serialization.random_str_input()
    return redirect(f"/level?heights={quote(heights_str)}&volume={quote(volume_str)}")


@app.get("/style.css")
async def get_style(request):
    return Template("style.css").render(), {
        "Content-Type": "text/css",
        "Max-Age": 3600 * 24,
    }
