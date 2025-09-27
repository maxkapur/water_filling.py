import io
from pathlib import Path
from urllib.parse import quote

import numpy as np
from microdot import Microdot, redirect
from microdot.jinja import Template

from . import water_filling

app = Microdot()
Template.initialize(Path(__file__).parent / "templates")


def volume_parser(s):
    try:
        res = np.fromstring(s, sep=",").item()
        if not res >= 0:
            raise ValueError
        return res
    except ValueError:
        return None


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


# TODO: Disk cache
def get_svg_data(heights, level):
    fig, ax = water_filling.visualize(heights, level)
    with io.StringIO() as buf:
        fig.savefig(buf, format="svg")
        return buf.getvalue()


@app.get("/level")
async def get_level(request):
    heights = heights_parser(request.args.get("heights"))
    volume = volume_parser(request.args.get("volume"))
    if heights is None or volume is None:
        return "Bad request", 400

    level = water_filling.level(heights, volume)
    svg_data = get_svg_data(heights, level)

    accept = request.headers.get("Accept", "").lower()

    if "text/html" in accept:
        return Template("visualize.html").render(
            heights_str=englishify(heights),
            volume_str=str(volume),
            level_str="%.2f" % level,
            svg_data=svg_data,
        ), {"Content-Type": "text/html"}

    if "image/svg" in accept:
        return svg_data

    # Default to JSON
    return {
        "heights": heights.tolist(),
        "volume": volume,
        "level": level,
        "svg": svg_data,
    }


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
