import json
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import pytest

from src.api import APIConnect
from src.plane import Plane
from src.processor import PlanesProcessor
from src.user_functions import UserFunction


@pytest.fixture
def api():
    return APIConnect()


@pytest.fixture
def osm_response():
    """Mock-ответ от OpenStreetMap."""
    resp = MagicMock()
    resp.json.return_value = [
        {
            "boundingbox": ["51.2", "51.8", "-0.5", "0.3"],
        }
    ]
    return resp


@pytest.fixture
def opensky_response():
    """Mock-ответ от OpenSky."""
    resp = MagicMock()
    resp.json.return_value = {
        "states": [["icao24", "callsign", "RU", ...]],
    }
    return resp


@pytest.fixture
def processor():
    return PlanesProcessor()


@pytest.fixture
def valid_item():
    item = [""] * 17
    item[0] = "model_A"
    item[1] = "Boeing"
    item[2] = "737"
    item[7] = "500"
    item[8] = "true"
    item[9] = "active"
    return item


@pytest.fixture
def plane_a():
    return Plane("P001", "AAL123", "USA", 35000.0, False, 500.0)


@pytest.fixture
def plane_b():
    return Plane("P002", "UAL456", "UK", 20000.0, True, 300.0)


@pytest.fixture
def plane_c():
    """Тот же speed, что у plane_a, но другие поля."""
    return Plane("P003", "DLH789", "Germany", 10000.0, False, 500.0)


@pytest.fixture
def fake_plane_class():
    """Подмена Plane простым dataclass с понятными полями и аннотациями."""

    @dataclass
    class FakePlane:
        model: str
        capacity: int
        airline: str = "Default"

    return FakePlane


@pytest.fixture
def sample_records():
    return [
        {"model": "Boeing 737", "capacity": 200, "airline": "Aeroflot"},
        {"model": "Airbus A320", "capacity": 180, "airline": "S7"},
        {"model": "Boeing 737", "capacity": 200, "airline": "S7"},
        {"model": "Airbus A350", "capacity": 300, "airline": "Aeroflot"},
    ]


@pytest.fixture
def json_file(tmp_path, sample_records):
    p = tmp_path / "planes.json"
    p.write_text(json.dumps(sample_records, ensure_ascii=False), encoding="utf-8")
    return str(p)


@pytest.fixture
def handler(fake_plane_class):
    """JsonFileHandler с подменённым Plane"""
    with patch("src.processor.Plane", fake_plane_class):
        import importlib

        import src.file_handler as fh_module

        importlib.reload(fh_module)
        yield fh_module.JsonFileHandler()


class FakePlane:
    """заглушка, совместимая с UserFunction"""

    def __init__(self, to_dict_data: dict):
        self._data = to_dict_data

    def to_dict(self) -> dict:
        return self._data


@pytest.fixture
def sample_planes():
    """Список из 4 самолётов с разными странами и высотами."""
    return [
        FakePlane({"reg_country": "RU", "height": 10000.0, "model": "Boeing 737"}),
        FakePlane({"reg_country": "US", "height": 5000.0, "model": "Airbus A320"}),
        FakePlane({"reg_country": "RU", "height": 12000.0, "model": "Tu-204"}),
        FakePlane({"reg_country": "CN", "height": 8000.0, "model": "C919"}),
    ]


@pytest.fixture
def sample_df(sample_planes):
    """Готовый DataFrame для тестов, которым не нужен полный pipeline."""
    user_func = UserFunction(sample_planes)
    return user_func.planes_to_dataframe()


@pytest.fixture
def user_func(sample_planes):
    return UserFunction(sample_planes)
