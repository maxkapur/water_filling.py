"""Build a static, nerfed version of the site to the `static/` directory.

The static site only has a single, hardcoded instance whose parameters are the
default (and read-only) values shown on the homepage form. Clicking "submit"
takes you to `level.html` which ignores the URL parameters and shows the
solution for this known instance. Random instances are disabled.
"""

import asyncio
from pathlib import Path

import numpy as np
from microdot.jinja import Template

from water_filling import database, serialization

heights = np.asanyarray([3, 5, 6, 8, 5, 1, 3])
volume = np.int_(19)


class StaticTemplate(Template):
    # Inherit from Template and modify a copy of its globals to minimize side
    # effects of importing or running this script.
    jinja_env = Template.jinja_env
    jinja_env.globals = Template.jinja_env.globals.copy()
    jinja_env.globals["static"] = True


async def render_index():
    heights_str = serialization.to_str(heights)
    volume_str = serialization.to_str(volume)

    return await StaticTemplate("form.html").render_async(
        heights_str=heights_str,
        volume_str=volume_str,
        errors=[],
    )


async def render_style():
    return await StaticTemplate("style.css").render_async()


async def render_level():
    response_dict = database.fulfill_as_json_serializable_skip_cache(heights, volume)
    return await Template("visualize.html").render_async(
        **response_dict,
    )


async def main(build_dir=Path(__file__).parent.parent / "static"):
    build_dir.mkdir(parents=True, exist_ok=True)

    dests = [
        build_dir / "index.html",
        build_dir / "style.css",
        build_dir / "level.html",
    ]
    coros = [render_index(), render_style(), render_level()]

    contents = await asyncio.gather(*coros)

    for dest, content in zip(dests, contents):
        with open(dest, "w") as f:
            f.write(content)
        print(f"{dest}: Wrote {len(content)} chars")


if __name__ == "__main__":
    asyncio.run(main())
