import pytest

from water_filling import static


@pytest.mark.asyncio
async def test_static(tmp_path):
    await static.main(tmp_path)
    assert (tmp_path / "style.css").is_file()
    assert (tmp_path / "index.html").is_file()
    assert (tmp_path / "level.html").is_file()
