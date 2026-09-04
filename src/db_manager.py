from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import psycopg2
from psycopg2 import extras, sql


class AbstractDBManager(ABC):
    @abstractmethod
    def connect(self, config: dict) -> None:
        pass

    @abstractmethod
    def write_once(self, data: List[Dict[str, Any]]) -> int:
        pass

    @abstractmethod
    def fetch_processed(
        self, query: str, params: Optional[Tuple] = None
    ) -> List[Dict[str, Any]]:
        pass


class DBManager(AbstractDBManager):

    # Маппинг: имя колонки в DataFrame → имя колонки в таблице planes
    COLUMN_MAP = {
        "planeID": "plane_id",
        "callsign": "callsign",
        "height": "height",
        "onground": "onground",
        "speed": "speed",
    }

    def __init__(self):
        self.conn = None
        self.cur = None

    def connect(self, config: dict) -> None:
        self.conn = psycopg2.connect(**config)
        self.cur = self.conn.cursor()
        self.cur.execute("SET search_path TO planestrackerapp")

    def _ensure_connected(self) -> None:
        if self.conn is None or self.conn.closed:
            raise RuntimeError(
                "Соединение с БД не установлено. Вызовите connect(config)."
            )

    # ─── публичный метод: точка входа ───

    def write_once(self, data: List[Dict[str, Any]]) -> int:
        """
        Разовая загрузка: страны → самолёты.
        data — список словарей вида:
            {'country_id': int, 'country_name': str, 'data': pd.DataFrame}

        Возвращает общее количество вставленных самолётов.
        """
        self._ensure_connected()

        if not data:
            return 0

        total_planes = 0

        with self.conn:  # одна транзакция на всё
            with self.conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE countries, planes RESTART IDENTITY CASCADE")

                for entry in data:
                    country_name = entry["country_name"]
                    df = entry["data"]

                    # Шаг 1: вставляем страну, получаем реальный country_id
                    cur.execute(
                        "INSERT INTO countries (name) VALUES (%s) RETURNING country_id",
                        (country_name,),
                    )
                    real_country_id = cur.fetchone()[0]

                    # Шаг 2: вставляем самолёты этой страны
                    inserted = self._insert_planes(cur, real_country_id, df)
                    total_planes += inserted

        return total_planes

    # ─── приватные методы ───

    def _insert_planes(self, cur, country_id: int, df: pd.DataFrame) -> int:
        """
        Вставляет DataFrame в таблицу planes с привязкой к country_id.
        Возвращает количество вставленных строк.
        """
        if df.empty:
            return 0

        # Формируем список колонок БД в нужном порядке
        df_cols = list(
            self.COLUMN_MAP.keys()
        )  # ['planeID', 'callsign', 'height', 'onground', 'speed']

        all_db_cols = [
            "plane_id",
            "callsign",
            "country_id",
            "height",
            "onground",
            "speed",
        ]


        insert_query = sql.SQL("""
                    INSERT INTO planes ({cols}) VALUES ({ph})
                    ON CONFLICT (plane_id) DO UPDATE SET
                        callsign  = EXCLUDED.callsign,
                        country_id = EXCLUDED.country_id,
                        height    = EXCLUDED.height,
                        onground   = EXCLUDED.onground,
                        speed     = EXCLUDED.speed
                """).format(
            cols=sql.SQL(", ").join([sql.Identifier(c) for c in all_db_cols]),
            ph=sql.SQL(", ").join([sql.Placeholder()] * len(all_db_cols)),
        )

        # Готовим значения: берём колонки из DataFrame + подставляем country_id
        values = []
        for _, row in df.iterrows():
            row_values = [row[col] for col in df_cols]  # 5 значений из DataFrame
            row_values.insert(2, country_id)  # вставляем country_id на 3-ю позицию
            values.append(tuple(row_values))

        cur.executemany(insert_query, values)
        return cur.rowcount

    def fetch_processed(self, query: str, params: Optional[Tuple] = None):
        """SELECT с обработкой — возвращает список словарей."""
        self._ensure_connected()

        with self.conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
            return pd.DataFrame(rows) if rows else pd.DataFrame()

    def get_countries_and_aeroplanes_count(self):
        query = """select c.*, count(p.plane_id) from countries as c
            join planes p using (country_id)
            group by country_id"""

        return self.fetch_processed(query)

    def get_all_aeroplanes(self):
        query = """select * from planes"""

        return self.fetch_processed(query)

    def get_avg_speed(self):
        query = """SELECT ROUND(AVG(speed), 2) AS avg_speed from planes"""

        return self.fetch_processed(query)

    def get_aeroplanes_with_higher_speed(self):
        query = """select * from planes
        where speed>(SELECT ROUND(AVG(speed), 2) AS avg_speed
        FROM planes)"""
        return self.fetch_processed(query)

    def get_aeroplanes_with_keyword(self, keyword):
        query = f"""select * from planes
        where lower(trim(callsign)) like '%{keyword.lower().strip()}%'"""
        return self.fetch_processed(query)
