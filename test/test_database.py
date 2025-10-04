import numpy as np

from water_filling import database


def test_fulfill_as_json_serializable_skip_cache(mock_db, triple):
    res = database.fulfill_as_json_serializable_skip_cache(
        np.asanyarray(triple.heights), np.asanyarray(triple.volume)[()]
    )
    assert res["heights"] == triple.heights
    assert res["volume"] == triple.volume
    assert np.isclose(res["level"], triple.level)
    assert isinstance(res["heights_repr"], str)
    assert isinstance(res["volume_repr"], str)
    assert isinstance(res["level_repr"], str)
    assert isinstance(res["svg"], str)
    assert res["cached"] is False
    assert res["bench"] is False


def test_fulfill_as_json_serializable_with_cache(mock_db, triple):
    res = database.fulfill_as_json_serializable_with_cache(
        np.asanyarray(triple.heights), np.asanyarray(triple.volume)[()]
    )
    assert res["heights"] == triple.heights
    assert res["volume"] == triple.volume
    assert np.isclose(res["level"], triple.level)
    assert isinstance(res["heights_repr"], str)
    assert isinstance(res["volume_repr"], str)
    assert isinstance(res["level_repr"], str)
    assert isinstance(res["svg"], str)
    assert res["cached"] is False
    assert res["bench"] is False

    res2 = database.fulfill_as_json_serializable_with_cache(
        np.asanyarray(triple.heights), np.asanyarray(triple.volume)[()]
    )
    assert res2["cached"] is True
    for key in res.keys():
        if key != "cached":
            assert res[key] == res2[key]
