import json

import numpy as np
import pytest
from microdot.test_client import TestClient

from water_filling import app


@pytest.mark.parametrize(
    "path,level",
    [
        ("/level/2/1,2,3,4", 2.5),
        ("/level/2/-1,2,-3,-4", -2.5),
    ],
)
@pytest.mark.asyncio
async def test_get_level_html(path, level):
    client = TestClient(app)
    resp = await client.get(path, headers={"Accept": "text/html"})
    assert resp.status_code == 200
    assert f"level of water is {level}" in resp.text


@pytest.mark.parametrize(
    "path,level",
    [
        ("/level/2/1,2,3,4", 2.5),
        ("/level/2/-1,2,-3,-4", -2.5),
    ],
)
@pytest.mark.asyncio
async def test_get_level_json(path, level):
    client = TestClient(app)
    resp = await client.get(path, headers={"Accept": "application/json"})
    assert resp.status_code == 200
    content = json.loads(resp.text)
    assert np.isclose(content["level"], level)
