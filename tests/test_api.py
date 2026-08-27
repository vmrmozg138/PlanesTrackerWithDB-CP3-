from unittest.mock import MagicMock, patch

import pytest


def test_returns_states(api, osm_response, opensky_response):
    with patch("src.api.get", side_effect=[osm_response, opensky_response]) as mock_get:
        result = api.get_data("Russia", "MyTestAgent/1.0")

    assert result == [["icao24", "callsign", "RU", ...]]
    assert mock_get.call_count == 2


def test_first_call_params(api, osm_response, opensky_response):
    with patch("src.api.get", side_effect=[osm_response, opensky_response]) as mock_get:
        api.get_data("Russia", "MyTestAgent/1.0")

    first_call = mock_get.call_args_list[0]
    assert first_call.args[0] == api.openstreetmap_url
    assert first_call.kwargs["params"]["country"] == "Russia"
    assert first_call.kwargs["params"]["format"] == "json"
    assert first_call.kwargs["params"]["limit"] == 1
    assert first_call.kwargs["headers"]["User-Agent"] == "MyTestAgent/1.0"


def test_second_call_params(api, osm_response, opensky_response):
    with patch("src.api.get", side_effect=[osm_response, opensky_response]) as mock_get:
        api.get_data("Russia", "MyTestAgent/1.0")

    second_call = mock_get.call_args_list[1]
    assert second_call.args[0] == api.opensky_url
    params = second_call.kwargs["params"]
    assert params["lamin"] == "51.2"
    assert params["lamax"] == "51.8"
    assert params["lomin"] == "-0.5"
    assert params["lomax"] == "0.3"


def test_sets_instance_attributes(api, osm_response, opensky_response):
    with patch("src.api.get", side_effect=[osm_response, opensky_response]):
        api.get_data("Germany", "AgentX")

    assert api.country == "Germany"
    assert api.useragent == "AgentX"
    assert api.params["country"] == "Germany"
    assert api.headers["User-Agent"] == "AgentX"


def test_empty_osm_response(api):
    osm_response = MagicMock()
    osm_response.json.return_value = []

    with patch("src.api.get", return_value=osm_response):
        with pytest.raises(IndexError):
            api.get_data("UnknownCountry", "Agent")


def test_missing_boundingbox(api):
    osm_response = MagicMock()
    osm_response.json.return_value = [{"lat": "55.0"}]

    with patch("src.api.get", return_value=osm_response):
        with pytest.raises(TypeError):
            api.get_data("SomeCountry", "Agent")


def test_missing_states_key(api):
    osm_response = MagicMock()
    osm_response.json.return_value = [{"boundingbox": ["1", "2", "3", "4"]}]
    opensky_response = MagicMock()
    opensky_response.json.return_value = {"time": 12345}

    with patch("src.api.get", side_effect=[osm_response, opensky_response]):
        with pytest.raises(KeyError):
            api.get_data("Russia", "Agent")
