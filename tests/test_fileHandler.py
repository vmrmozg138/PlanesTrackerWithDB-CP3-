import json
import pytest
from src.file_handler import AbstractFileHandler, JsonFileHandler


def test_cannot_instantiate_abstract():
    with pytest.raises(TypeError):
        AbstractFileHandler()


def test_subclass_must_implement_all_abstract():
    class Incomplete(AbstractFileHandler):
        def read(self):
            pass

    with pytest.raises(TypeError):
        Incomplete()


def test_delete_is_not_abstract():
    assert "delete" not in AbstractFileHandler.__abstractmethods__


def test_read_returns_list_of_dicts(handler, json_file):
    data = handler.read(json_file)
    assert isinstance(data, list)
    assert all(isinstance(row, dict) for row in data)
    assert len(data) == 4


def test_read_content_matches(handler, json_file, sample_records):
    assert handler.read(json_file) == sample_records


def test_read_nonexistent_file(handler):
    with pytest.raises(FileNotFoundError):
        handler.read("nonexistent_file.json")


def test_read_empty_json_file(handler, tmp_path):
    p = tmp_path / "empty.json"
    p.write_text("[]", encoding="utf-8")
    assert handler.read(str(p)) == []


def test_write_creates_file(handler, tmp_path):
    data = [{"model": "Test", "capacity": 100, "airline": "X"}]
    out = str(tmp_path / "out.json")
    handler.write(data, out)
    with open(out, encoding="utf-8") as f:
        assert json.load(f) == data


def test_write_preserves_unicode(handler, tmp_path):
    data = [{"model": "Самолёт", "capacity": 100, "airline": "Аэрофлот"}]
    out = str(tmp_path / "unicode.json")
    handler.write(data, out)
    raw = open(out, encoding="utf-8").read()
    assert "Самолёт" in raw
    assert "Аэрофлот" in raw


def test_write_overwrites_existing(handler, tmp_path):
    out = str(tmp_path / "over.json")
    handler.write([{"a": 1}], out)
    handler.write([{"b": 2}], out)
    with open(out, encoding="utf-8") as f:
        assert json.load(f) == [{"b": 2}]


def test_validate_valid_params_pass(handler):
    handler._validate_params({"model": "Boeing", "capacity": 200})


def test_validate_unknown_param_raises(handler):
    with pytest.raises(ValueError, match="Неизвестный параметр"):
        handler._validate_params({"unknown_field": 1})


def test_validate_wrong_type_raises(handler):
    with pytest.raises(ValueError, match="ожидает int"):
        handler._validate_params({"capacity": "not_a_number"})


def test_validate_empty_params_pass(handler):
    handler._validate_params({})


def test_validate_multiple_errors_reports_first(handler):
    with pytest.raises(ValueError, match="Неизвестный параметр 'xxx'"):
        handler._validate_params({"xxx": 1, "yyy": 2})


def test_validate_optional_field_validates(handler):
    handler._validate_params({"airline": "Aeroflot"})


def test_all_single_match(handler, json_file, fake_plane_class):
    result = handler.get_advanced_all(json_file, {"model": "Boeing 737"})
    assert len(result) == 2
    assert all(isinstance(p, fake_plane_class) for p in result)
    assert all(p.model == "Boeing 737" for p in result)


def test_all_multiple_conditions(handler, json_file):
    result = handler.get_advanced_all(
        json_file, {"model": "Boeing 737", "airline": "S7"}
    )
    assert len(result) == 1
    assert result[0].airline == "S7"


def test_all_no_match(handler, json_file):
    assert handler.get_advanced_all(json_file, {"model": "Tu-154"}) == []


def test_all_empty_params_returns_all(handler, json_file):
    assert len(handler.get_advanced_all(json_file, {})) == 4


def test_all_invalid_param_raises(handler, json_file):
    with pytest.raises(ValueError):
        handler.get_advanced_all(json_file, {"nonexistent": 1})


def test_any_single_match(handler, json_file):
    result = handler.get_advanced_any(json_file, {"airline": "S7"})
    assert len(result) == 2
    assert all(p.airline == "S7" for p in result)


def test_any_multiple_conditions(handler, json_file):
    result = handler.get_advanced_any(
        json_file, {"model": "Airbus A350", "airline": "S7"}
    )
    # Airbus A350 → 1, airline=S7 → 2, пересечений нет → 3
    assert len(result) == 3


def test_any_no_match(handler, json_file):
    assert handler.get_advanced_any(json_file, {"model": "Tu-154"}) == []


def test_any_empty_params_returns_all(handler, json_file):
    assert len(handler.get_advanced_any(json_file, {})) == 4


def test_any_invalid_param_raises(handler, json_file):
    with pytest.raises(ValueError):
        handler.get_advanced_any(json_file, {"bad_field": 1})


def test_delete_removes_matching(handler, json_file):
    handler.delete(None, json_file, {"model": "Boeing 737"})
    remaining = handler.read(json_file)
    assert "Boeing 737" not in [r["model"] for r in remaining]
    assert len(remaining) == 2


def test_delete_no_match_keeps_all(handler, json_file):
    handler.delete(None, json_file, {"model": "Tu-154"})
    assert len(handler.read(json_file)) == 4


def test_delete_multiple_conditions(handler, json_file):
    """OR: airline=S7 ИЛИ model=Airbus A350 → остаётся 1 запись."""
    handler.delete(None, json_file, {"airline": "S7", "model": "Airbus A350"})
    remaining = handler.read(json_file)
    assert len(remaining) == 1
    assert remaining[0]["model"] == "Boeing 737"
    assert remaining[0]["airline"] == "Aeroflot"


def test_delete_empty_params(handler, json_file):
    handler.delete(None, json_file, {})
    assert len(handler.read(json_file)) == 4


def test_delete_writes_file(handler, json_file):
    handler.delete(None, json_file, {"airline": "Aeroflot"})
    remaining = handler.read(json_file)
    assert all(r["airline"] != "Aeroflot" for r in remaining)
    assert len(remaining) == 2


def test_delete_invalid_param_raises(handler, json_file):
    with pytest.raises(ValueError):
        handler.delete(None, json_file, {"wrong": 1})
