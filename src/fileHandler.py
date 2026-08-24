import json
from abc import ABC, abstractmethod
from src.processor import Plane
import inspect
import Pandas as

class AbstractFileHandler(ABC):

    @abstractmethod
    def read(self):
        pass
    @abstractmethod
    def get_data_advanced(self):
        pass
    @abstractmethod
    def write(self):
        pass
    def delete(self):
        pass


class JsonFileHandler(AbstractFileHandler):

    def __init__(self):
        pass

    def read(self, filename: str):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data

    def get_data_advanced(self, filename: str, **params):
        data = self.read(filename)
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
                if expected is int and isinstance(value, bool):
                    raise ValueError(
                        f"Параметр '{key}' ожидает int, получен bool"
                    )
                if not isinstance(value, expected):
                    raise ValueError(
                        f"Параметр '{key}' ожидает {expected.__name__}, "
                        f"получен {type(value).__name__}"
                    )

        planes = [Plane(**item) for item in data]

        return [
            plane for plane in planes
            if all(getattr(plane, key) == value for key, value in params.items())
        ]

    def write(self, data, filename: str):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def delete(self, data, filename: str):
        pass

