import pandas as pd

from src.plane import Plane


class UserFunction:
    def __init__(self, planes: list[Plane]):
        self.__planes = planes

    def planes_to_dataframe(self):
        return pd.DataFrame([p.to_dict() for p in self.__planes])

    def filter_planes(self, df: pd.DataFrame, filter_words: list):
        return df[df["reg_country"].isin(filter_words)].reset_index(drop=True)

    def get_planes_by_altitude(self, df: pd.DataFrame, altitude_range: str):

        parts = altitude_range.split("-")
        min_h = float(parts[0].strip())
        max_h = float(parts[1].strip())

        return df[(df["height"] >= min_h) & (df["height"] <= max_h)].reset_index(
            drop=True
        )

    def sort_planes(self, df: pd.DataFrame, ascending: bool = True):
        return df.sort_values(by="height", ascending=ascending).reset_index(drop=True)

    def get_top_planes(self, df: pd.DataFrame, top_n: int):
        return df.head(top_n)
