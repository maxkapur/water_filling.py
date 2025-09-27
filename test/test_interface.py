import json

import numpy as np
import pytest
from microdot.test_client import TestClient

from water_filling import app


def to_level_path(triple):
    heights_str = ",".join(str(x) for x in triple.heights)
    return f"/level/{triple.volume}/{heights_str}"


@pytest.mark.asyncio
async def test_get_level_html(triple):
    path = to_level_path(triple)
    client = TestClient(app)
    resp = await client.get(path, headers={"Accept": "text/html"})
    assert resp.status_code == 200

    if np.isclose(triple.level, 0.0, atol=1e-5):
        assert (
            f"level of water is {triple.level}" in resp.text
            or f"level of water is -{triple.level}" in resp.text
        )
    else:
        assert f"level of water is {triple.level}" in resp.text


@pytest.mark.asyncio
async def test_get_level_svg(triple):
    path = to_level_path(triple)
    client = TestClient(app)
    resp = await client.get(path, headers={"Accept": "image/svg"})
    assert resp.status_code == 200
    assert "http://www.w3.org/2000/svg" in resp.text
    assert resp.text.lower().strip().endswith("</svg>")


@pytest.mark.asyncio
async def test_get_level_json(triple):
    path = to_level_path(triple)
    client = TestClient(app)
    resp = await client.get(path, headers={"Accept": "application/json"})
    assert resp.status_code == 200
    content = json.loads(resp.text)
    assert np.isclose(content["level"], triple.level, atol=1e-5)
