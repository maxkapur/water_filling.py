import numpy as np
from microdot import Microdot

import water_filling

app = Microdot()


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


@app.get("/level/<volume>/<heights>")
async def get(request, volume, heights):
    volume = volume_parser(volume)
    heights = heights_parser(heights)
    if volume is None or heights is None:
        return "Bad request", 400

    level = water_filling.level(heights, volume)
    return f"{volume = }, {heights = }, {level = }"


if __name__ == "__main__":
    app.run()
