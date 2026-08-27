import pandas as pd
import pytest

from src.user_functions import UserFunction


def test_planes_to_dataframe_returns_dataframe(user_func):
    df = user_func.planes_to_dataframe()
    assert isinstance(df, pd.DataFrame)


def test_planes_to_dataframe_correct_rows(user_func, sample_planes):
    df = user_func.planes_to_dataframe()
    assert len(df) == len(sample_planes)


def test_planes_to_dataframe_columns(user_func):
    df = user_func.planes_to_dataframe()
    assert set(df.columns) == {"reg_country", "height", "model"}


def test_planes_to_dataframe_empty_list():
    user_func = UserFunction([])
    df = user_func.planes_to_dataframe()
    assert df.empty
    assert isinstance(df, pd.DataFrame)


def test_filter_planes_by_country(user_func, sample_df):
    result = user_func.filter_planes(sample_df, ["RU"])
    assert set(result["reg_country"]) == {"RU"}
    assert len(result) == 2


def test_filter_planes_multiple_countries(user_func, sample_df):
    result = user_func.filter_planes(sample_df, ["RU", "US"])
    assert set(result["reg_country"]) == {"RU", "US"}
    assert len(result) == 3


def test_filter_planes_no_match(user_func, sample_df):
    result = user_func.filter_planes(sample_df, ["DE"])
    assert result.empty


def test_filter_planes_empty_filter_list(user_func, sample_df):
    result = user_func.filter_planes(sample_df, [])
    assert result.empty


def test_filter_planes_reset_index(user_func, sample_df):
    result = user_func.filter_planes(sample_df, ["RU"])
    assert list(result.index) == [0, 1]


def test_get_planes_by_altitude_range(user_func, sample_df):
    result = user_func.get_planes_by_altitude(sample_df, "5000-10000")
    assert all(result["height"] >= 5000.0)
    assert all(result["height"] <= 10000.0)
    assert len(result) == 3


def test_get_planes_by_altitude_exact_boundaries(user_func, sample_df):
    """Границы включены (>=, <=)."""
    result = user_func.get_planes_by_altitude(sample_df, "5000-10000")
    assert 5000.0 in result["height"].values
    assert 10000.0 in result["height"].values


def test_get_planes_by_altitude_with_spaces(user_func, sample_df):
    result = user_func.get_planes_by_altitude(sample_df, " 5000 - 10000 ")
    assert len(result) == 3


def test_get_planes_by_altitude_no_match(user_func, sample_df):
    result = user_func.get_planes_by_altitude(sample_df, "20000-30000")
    assert result.empty


def test_get_planes_by_altitude_reset_index(user_func, sample_df):
    result = user_func.get_planes_by_altitude(sample_df, "5000-10000")
    assert list(result.index) == list(range(len(result)))


def test_sort_planes_ascending(user_func, sample_df):
    result = user_func.sort_planes(sample_df, ascending=True)
    heights = result["height"].tolist()
    assert heights == sorted(heights)


def test_sort_planes_descending(user_func, sample_df):
    result = user_func.sort_planes(sample_df, ascending=False)
    heights = result["height"].tolist()
    assert heights == sorted(heights, reverse=True)


def test_sort_planes_default_ascending(user_func, sample_df):
    result = user_func.sort_planes(sample_df)
    assert result["height"].iloc[0] <= result["height"].iloc[-1]


def test_sort_planes_reset_index(user_func, sample_df):
    result = user_func.sort_planes(sample_df)
    assert list(result.index) == list(range(len(result)))


def test_get_top_planes_n2(user_func, sample_df):
    result = user_func.get_top_planes(sample_df, 2)
    assert len(result) == 2


def test_get_top_planes_more_than_available(user_func, sample_df):
    result = user_func.get_top_planes(sample_df, 100)
    assert len(result) == len(sample_df)


def test_get_top_planes_zero(user_func, sample_df):
    result = user_func.get_top_planes(sample_df, 0)
    assert result.empty


def test_get_top_planes_preserves_order(user_func, sample_df):
    """Top-N возвращает строки из начала DataFrame без перестановки."""
    sorted_df = user_func.sort_planes(sample_df, ascending=False)
    result = user_func.get_top_planes(sorted_df, 2)
    assert result["height"].tolist() == [12000.0, 10000.0]
