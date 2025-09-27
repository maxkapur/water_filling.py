import io
from pathlib import Path

import numpy as np
from microdot import Microdot
from microdot.jinja import Template

import water_filling

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


def stringify(list_of_numbers):
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


@app.get("/level/<volume>/<heights>")
async def get(request, volume, heights):
    volume = volume_parser(volume)
    heights = heights_parser(heights)
    if volume is None or heights is None:
        return "Bad request", 400

    level = water_filling.level(heights, volume)

    accept = request.headers.get("Accept", "").lower()
    if "text/html" in accept:
        fig, ax = water_filling.visualize(heights, level)
        with io.StringIO() as buf:
            fig.savefig(buf, format="svg")
            return Template("visualize.html").render(
                heights_str=stringify(heights),
                volume_str=str(volume),
                level_str="%.2f" % level,
                svg_data=buf.getvalue(),
            ), {"Content-Type": "text/html"}
    if "image/svg" in accept:
        # TODO
        return "Bad request", 400
    else:  # json
        return {"volume": volume, "heights": heights.tolist(), "level": level}
