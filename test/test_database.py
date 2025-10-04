import numpy as np

from water_filling import database


def test_database(mock_db, triple):
    res = database.get_level_as_dict_from_parsed(
        np.asanyarray(triple.heights), np.asanyarray(triple.volume)[()]
    )
    assert res["heights"] == triple.heights
    assert res["volume"] == triple.volume
    assert np.isclose(res["level"], triple.level)
    assert res["heights_repr"]
    assert res["volume_repr"]
    assert res["level_repr"]
    assert res["svg"]
    assert res["cached"] is False

    res2 = database.get_level_as_dict_from_parsed(
        np.asanyarray(triple.heights), np.asanyarray(triple.volume)[()]
    )
    assert res2["cached"] is True
    for key in res.keys():
        if key != "cached":
            assert res[key] == res2[key]
