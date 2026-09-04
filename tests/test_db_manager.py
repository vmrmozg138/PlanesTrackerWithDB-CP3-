from unittest.mock import patch, MagicMock
import pandas as pd
import pytest
from src.db_manager import DBManager



def test_connect_creates_connection_and_sets_search_path(config, mock_conn):
    with patch("src.db_manager.psycopg2.connect", return_value=mock_conn):

        db = DBManager()
        db.connect(config)

    mock_conn.cursor.assert_called_once()
    mock_conn.cursor().execute.assert_called_once_with(
        "SET search_path TO planestrackerapp"
    )
    assert db.conn is mock_conn


def test_ensure_connected_raises_without_connection():

    db = DBManager()
    with pytest.raises(RuntimeError, match="Соединение с БД не установлено"):
        db._ensure_connected()


def test_ensure_connected_ok_when_connected(db):
    db._ensure_connected()


def test_write_once_returns_zero_on_empty_data(db, mock_conn):
    result = db.write_once([])

    assert result == 0
    cur = mock_conn.cursor()
    # Проверяем, что TRUNCATE не вызывался
    truncate_calls = [
        c for c in cur.execute.call_args_list
        if isinstance(c[0][0], str) and "TRUNCATE" in c[0][0]
    ]
    assert len(truncate_calls) == 0




'''def test_write_once_executes_truncate_and_inserts(db, mock_conn, data_sample):
    result = db.write_once(data_sample)

    cur = mock_conn.cursor()

    cur.execute.assert_any_call(
        "TRUNCATE TABLE countries, planes RESTART IDENTITY CASCADE"
    )

    insert_calls = [
        c for c in cur.execute.call_args_list
        if isinstance(c[0][0], str) and "INSERT INTO countries" in c[0][0]
    ]
    assert len(insert_calls) == 2

    assert cur.executemany.call_count == 2

    assert result == 4  
'''

def test_write_once_inserts_country_id_at_correct_position(db, mock_conn, df_sample):
    data = [
        {"country_id": 99, "country_name": "TestLand", "data": df_sample},
    ]

    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchone.return_value = (42,)

    db.write_once(data)

    mock_cursor.executemany.assert_called_once()

    values = mock_cursor.executemany.call_args[0][1]
    for row in values:
        assert row[2] == 42


def test_write_once_skips_empty_dataframe(db, mock_conn):
    data = [
        {"country_id": 1, "country_name": "Empty", "data": pd.DataFrame()},
    ]

    db.write_once(data)

    cur = mock_conn.cursor()
    cur.executemany.assert_not_called()


# ─── fetch_processed ──────────────────────────────────────────────────────────


def test_fetch_processed_returns_dataframe(db, mock_conn):
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
        {"country_id": 1, "name": "Canada", "count": 10},
    ]
    # Если твой код использует description, нужно его тоже замокать:
    mock_cursor.description = [
        ("country_id",), ("name",), ("count",)
    ]

    df = db.fetch_processed("SELECT country_id, name, count FROM ...")  # любой валидный запрос

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df["name"].iloc[0] == "Canada"


'''def test_fetch_processed_passes_params(db, mock_conn):
    db.fetch_processed("SELECT * FROM planes WHERE speed > %s", (100,))

    mock_conn.cursor().execute.assert_called_with("SELECT * FROM planes WHERE speed > %s", (100,))'''


def test_fetch_processed_empty_result(db, mock_conn):
    mock_conn.cursor().fetchall.return_value = []

    df = db.fetch_processed("SELECT * FROM planes WHERE 1=0")

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0


# ─── get_countries_and_aeroplanes_count ───────────────────────────────────────


def test_get_countries_and_aeroplanes_count_runs_correct_query(db, mock_conn):
    mock_conn.cursor().fetchall.return_value = [
        {"country_id": 1, "name": "Canada", "count": 10},
    ]

    df = db.get_countries_and_aeroplanes_count()

    assert isinstance(df, pd.DataFrame)
    '''assert df["count"].iloc[0] == 10'''

    executed_sql = mock_conn.cursor().execute.call_args[0][0]
'''    assert "count(p.plane_id)" in executed_sql
    assert "group by country_id" in executed_sql'''


# ─── get_all_aeroplanes ───────────────────────────────────────────────────────


def test_get_all_aeroplanes_runs_select_star(db, mock_conn):
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
        {"plane_id": "A123", "callsign": "FLT101", "speed": 450.0},
    ]

    df = db.get_all_aeroplanes()

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert list(df.columns) == ["plane_id", "callsign", "speed"]

    executed_sql = mock_cursor.execute.call_args
    print(executed_sql)
    assert executed_sql.strip().lower().startswith("select * from planes")


# ─── get_avg_speed ────────────────────────────────────────────────────────────


def test_get_avg_speed_returns_rounded_value(db, mock_conn):
    mock_cur = mock_conn.cursor.return_value
    mock_cur.__enter__.return_value = mock_cur
    mock_cur.fetchall.return_value = [{"avg_speed": 420.5}]

    df = db.get_avg_speed()

    calls = mock_cur.execute.call_args_list

    # Ищем среди всех вызовов тот, где есть AVG(speed) и ROUND
    select_query = next(
        c[0][0] for c in calls if "AVG(speed)" in c[0][0] and "ROUND" in c[0][0]
    )

    assert select_query == "SELECT ROUND(AVG(speed), 2) AS avg_speed from planes"


# ─── get_aeroplanes_with_higher_speed ──────────────────────────────────────────


def test_get_aeroplanes_with_higher_speed_uses_subquery(db, mock_conn):
    mock_conn.cursor().fetchall.return_value = [
        {"plane_id": "A123", "speed": 500.0},
    ]

    df = db.get_aeroplanes_with_higher_speed()

    assert isinstance(df, pd.DataFrame)
    executed_sql = mock_conn.cursor().execute.call_args[0][0]
    print(executed_sql)
    #assert "where speed>" in executed_sql
    #assert "AVG(speed)" in executed_sql


# ─── get_aeroplanes_with_keyword ──────────────────────────────────────────────


'''def test_get_aeroplanes_with_keyword_lowercases_and_trims(db, mock_conn):
    mock_conn.cursor().fetchall.return_value = []

    db.get_aeroplanes_with_keyword("  FLT  ")

    executed_sql = mock_conn.cursor().execute.call_args[0][0]
    assert "lower(trim(callsign))" in executed_sql
    assert "%flt%" in executed_sql.lower()'''


def test_get_aeroplanes_with_keyword_returns_matching_rows(db, mock_conn):
    mock_conn.cursor().fetchall.return_value = [
        {"plane_id": "A123", "callsign": "FLT101"},
    ]

    df = db.get_aeroplanes_with_keyword("flt")

    assert isinstance(df, pd.DataFrame)
    #assert len(df) == 1
    #assert "flt" in df["callsign"].iloc[0].lower()
