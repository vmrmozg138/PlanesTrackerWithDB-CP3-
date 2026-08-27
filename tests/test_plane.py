import pytest

from src.plane import Plane


def test_to_dict_contains_all_keys(plane_a):
    d = plane_a.to_dict()
    assert set(d.keys()) == {
        "planeID",
        "callsign",
        "reg_country",
        "height",
        "onground",
        "speed",
    }


def test_to_dict_values_match_init(plane_a):
    d = plane_a.to_dict()
    assert d["planeID"] == "P001"
    assert d["callsign"] == "AAL123"
    assert d["reg_country"] == "USA"
    assert d["height"] == 35000.0
    assert d["onground"] is False
    assert d["speed"] == 500.0


def test_eq_same_speed(plane_a, plane_c):
    assert plane_a == plane_c


def test_ne_different_speed(plane_a, plane_b):
    assert plane_a != plane_b


def test_lt(plane_b, plane_a):
    assert plane_b < plane_a


def test_gt(plane_a, plane_b):
    assert plane_a > plane_b


def test_le_same_speed(plane_a, plane_c):
    assert plane_a <= plane_c


def test_le_less_speed(plane_b, plane_a):
    assert plane_b <= plane_a


def test_ge_same_speed(plane_a, plane_c):
    assert plane_a >= plane_c


def test_ge_greater_speed(plane_a, plane_b):
    assert plane_a >= plane_b


def test_is_higher_than_true(plane_a, plane_b):
    assert plane_a.is_higher_than(plane_b) is True


def test_is_higher_than_false(plane_b, plane_a):
    assert plane_b.is_higher_than(plane_a) is False


def test_is_lower_than_true(plane_b, plane_a):
    assert plane_b.is_lower_than(plane_a) is True


def test_is_lower_than_false(plane_a, plane_b):
    assert plane_a.is_lower_than(plane_b) is False


def test_is_higher_than_equal_height():
    p1 = Plane("X", "CS1", "RU", 10000.0, False, 100.0)
    p2 = Plane("Y", "CS2", "RU", 10000.0, True, 200.0)
    assert p1.is_higher_than(p2) is False
    assert p1.is_lower_than(p2) is False
