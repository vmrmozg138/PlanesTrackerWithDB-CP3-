import inspect
import json
from abc import ABC, abstractmethod
from typing import Any, cast

import pandas as pd

from src.processor import Plane


class AbstractFileHandler(ABC):

    @abstractmethod
    def read(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_advanced_all(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_advanced_any(self, *args, **kwargs):
        pass

    @abstractmethod
    def write(self, *args, **kwargs):
        pass

    def delete(self, *args, **kwargs):
        pass


class JsonFileHandler(AbstractFileHandler):

    def __init__(self):
        pass

    def read(self, filename: str):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data

    def _validate_params(self, params: dict) -> None:
        sig = inspect.signature(Plane.__init__)
        valid_fields = set(sig.parameters.keys()) - {"self"}
        type_hints = {
            name: p.annotation
            for name, p in sig.parameters.items()
            if name != "self" and p.annotation is not inspect.Parameter.empty
        }
        for key, value in params.items():
            if key not in valid_fields:
                raise ValueError(
                    f"Неизвестный параметр '{key}'. "
                    f"Допустимые: {', '.join(sorted(valid_fields))}"
                )
            if key in type_hints:
                expected = type_hints[key]
                """if expected is int and isinstance(value, bool):
                    raise ValueError(
                        f"Параметр '{key}' ожидает int, получен bool"
                    )"""
                if not isinstance(value, expected):
                    raise ValueError(
                        f"Параметр '{key}' ожидает {expected.__name__}, "
                        f"получен {type(value).__name__}"
                    )

    def get_advanced_all(self, filename: str, params: dict):

        self._validate_params(params)

        data = self.read(filename)
        df = pd.DataFrame(data)

        if params:
            mask = pd.Series([True] * len(df))
            for k, v in params.items():
                mask &= df[k] == v
            df = df[mask]

        return [Plane(**cast(dict[str, Any], row)) for row in df.to_dict("records")]

    def get_advanced_any(self, filename: str, params: dict):

        self._validate_params(params)

        data = self.read(filename)
        df = pd.DataFrame(data)

        if params:
            mask = pd.Series([False] * len(df))
            for k, v in params.items():
                mask |= df[k] == v
            df = df[mask]

        return [Plane(**cast(dict[str, Any], row)) for row in df.to_dict("records")]

    def write(self, data, filename: str):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def delete(self, data, filename: str, params: dict):
        self._validate_params(params)

        data = self.read(filename)
        df = pd.DataFrame(data)

        if params:
            mask = pd.Series([False] * len(df))
            for k, v in params.items():
                mask |= df[k] == v
            df = df[~mask]

        result = df.to_dict("records")
        self.write(result, filename)
