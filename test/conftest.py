import sqlite3
from collections import namedtuple

import pytest
from microdot.test_client import TestClient

from water_filling import app, database

WaterFillingTriple = namedtuple("WaterFillingTriple", "heights volume level".split())


@pytest.fixture(
    scope="module",
    params=[
        WaterFillingTriple([1, 2, 3, 4], 0.0, 1.0),
        WaterFillingTriple([1, 2, 3, 4], 0.5, 1.5),
        WaterFillingTriple([1, 2, 3, 4], 2.0, 2.5),
        WaterFillingTriple([1, 2, 3, 4], 6.0, 4.0),
        WaterFillingTriple([1, 2, 3, 4], 30.0, 10.0),
        WaterFillingTriple([-1, 2, -3, -4], 0.0, -4.0),
        WaterFillingTriple([-1, 2, -3, -4], 0.5, -3.5),
        WaterFillingTriple([-1, 2, -3, -4], 8.0, 0.0),
        WaterFillingTriple([-1, 2, -3, -4], 12.5, 1.5),
        WaterFillingTriple([-1, 2, -3, -4], 14.0, 2.0),
        WaterFillingTriple([-1, 2, -3, -4], 18.0, 3.0),
        WaterFillingTriple([4, 4, 4, 4], 0.0, 4.0),
        WaterFillingTriple([4, 4, 4, 4], 8.0, 6.0),
    ],
)
def triple(request):
    """Triple of valid `heights`, `volume`, and `level` for water filling."""
    yield request.param


@pytest.fixture(scope="function")
def mock_db(monkeypatch, tmp_path):
    """Fixture that mocks the DB to a temporary file to test caching."""
    db_path = tmp_path / "water_filling.cache.db"
    con = sqlite3.connect(db_path)
    with monkeypatch.context() as m:
        m.setattr(database, "con", con)
        yield


@pytest.fixture(scope="function")
def client(mock_db):
    yield TestClient(app)
