import json
import re

import numpy as np
import pytest

from water_filling import serialization


@pytest.mark.asyncio
async def test_get_level_html(client, triple):
    path = serialization.to_path(triple.heights, triple.volume)
    resp = await client.get(path, headers={"Accept": "text/html"})
    assert resp.status_code == 200
    # Not cached (depends on correct monkeypatching in conftest.py)
    assert "cache" not in resp.text

    # Computed level is always an np.float64
    level_esc = re.escape(str(float(triple.level)))
    if np.isclose(triple.level, 0.0):
        assert re.search(rf"<strong>-?{level_esc}\d*</strong>", resp.text), level_esc
    else:
        assert re.search(rf"<strong>{level_esc}\d*</strong>", resp.text), level_esc

    # Issue the same request again, ensure it was pulled from cache
    resp2 = await client.get(path, headers={"Accept": "text/html"})
    assert resp2.status_code == 200
    assert "cache" in resp2.text


@pytest.mark.asyncio
async def test_get_level_svg(client, triple):
    path = serialization.to_path(triple.heights, triple.volume)
    resp = await client.get(path, headers={"Accept": "image/svg"})
    assert resp.status_code == 200
    assert "http://www.w3.org/2000/svg" in resp.text
    assert resp.text.lower().strip().endswith("</svg>")


@pytest.mark.asyncio
async def test_get_level_json(client, triple):
    path = serialization.to_path(triple.heights, triple.volume)
    resp = await client.get(path, headers={"Accept": "application/json"})
    assert resp.status_code == 200
    content = json.loads(resp.text)
    assert content["heights"] == triple.heights
    assert content["volume"] == triple.volume
    assert np.isclose(content["level"], triple.level)
    assert "http://www.w3.org/2000/svg" in content["svg"]
    assert content["cached"] is False

    # Issue the same request again, ensure it was pulled from cache
    resp2 = await client.get(path, headers={"Accept": "application/json"})
    assert resp2.status_code == 200
    content2 = json.loads(resp2.text)
    assert content2["heights"] == triple.heights
    assert content2["volume"] == triple.volume
    assert np.isclose(content2["level"], triple.level)
    assert "http://www.w3.org/2000/svg" in content2["svg"]
    assert content2["cached"] is True


@pytest.mark.asyncio
async def test_get_random_html(client):
    path = "/random"
    resp = await client.get(path, headers={"Accept": "text/html"})
    assert resp.status_code == 200
    assert "cache" not in resp.text
    assert re.search(r"level\s+of\s+water\s+is\s+<strong>[\-\.\d]+</strong>", resp.text)


@pytest.mark.asyncio
async def test_get_random_svg(client):
    path = "/random"
    resp = await client.get(path, headers={"Accept": "image/svg"})
    assert resp.status_code == 200
    assert "http://www.w3.org/2000/svg" in resp.text
    assert resp.text.lower().strip().endswith("</svg>")


@pytest.mark.asyncio
async def test_get_random_json(client):
    path = "/random"
    resp = await client.get(path, headers={"Accept": "application/json"})
    assert resp.status_code == 200
    content = json.loads(resp.text)
    assert isinstance(content["heights"], list)
    assert all(isinstance(x, int) for x in content["heights"])
    assert isinstance(content["volume"], int)
    assert isinstance(content["level"], float)
    assert "heights_repr" not in content
    assert "volume_repr" not in content
    assert "level_repr" not in content
    assert "http://www.w3.org/2000/svg" in content["svg"]
    assert content["cached"] is False
