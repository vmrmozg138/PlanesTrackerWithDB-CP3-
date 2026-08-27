import pytest


def test_valid_item_returns_true(processor, valid_item):
    assert processor.validate_item(valid_item) is True


def test_wrong_length_returns_false(processor, valid_item):
    assert processor.validate_item(valid_item[:10]) is False


def test_empty_list_returns_false(processor):
    assert processor.validate_item([]) is False


@pytest.mark.parametrize("index", [0, 1, 2, 7, 8, 9])
def test_empty_required_field_returns_false(processor, valid_item, index):
    item = valid_item.copy()
    item[index] = ""
    assert processor.validate_item(item) is False


@pytest.mark.parametrize("index", [0, 1, 2, 7, 8, 9])
def test_whitespace_required_field_returns_false(processor, valid_item, index):
    item = valid_item.copy()
    item[index] = "   "
    assert processor.validate_item(item) is False


@pytest.mark.parametrize("value", ["true", "TRUE", "True", "false", "False", "FALSE"])
def test_index8_accepts_true_false_case_insensitive(processor, valid_item, value):
    item = valid_item.copy()
    item[8] = value
    assert processor.validate_item(item) is True


@pytest.mark.parametrize("value", ["yes", "no", "1", "0", "t", "f", ""])
def test_index8_rejects_invalid_values(processor, valid_item, value):
    item = valid_item.copy()
    item[8] = value
    assert processor.validate_item(item) is False


def test_valid_items_become_planes(processor, valid_item):
    result = processor.transform_to_objects([valid_item])
    assert len(result) == 1


def test_invalid_items_skipped(processor, valid_item):
    bad_item = valid_item.copy()
    bad_item[8] = "maybe"
    result = processor.transform_to_objects([valid_item, bad_item])
    assert len(result) == 1


def test_all_invalid_returns_empty(processor):
    bad = [""] * 17
    result = processor.transform_to_objects([bad])
    assert result == []


def test_empty_input_returns_empty(processor):
    result = processor.transform_to_objects([])
    assert result == []


def test_returns_self_planes(processor, valid_item):
    result = processor.transform_to_objects([valid_item])
    assert result is processor.planes
