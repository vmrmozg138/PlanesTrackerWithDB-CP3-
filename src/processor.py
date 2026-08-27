from abc import ABC, abstractmethod

from src.plane import Plane


class AbstractPlanesProcessor(ABC):
    @abstractmethod
    def transform_to_objects(self, *args, **kwargs):
        pass


class PlanesProcessor(AbstractPlanesProcessor):
    def __init__(self):
        self.indices = [0, 1, 2, 7, 8, 9]
        self.planes = []

    def validate_item(self, input_data: list):
        if len(input_data) != 17:
            return False
        if any(str(input_data[i]).strip() == "" for i in self.indices):
            return False
        if str(input_data[8]).strip().lower() not in ["true", "false"]:
            return False
        return True

    def transform_to_objects(self, input_data: list[list]):
        for item in input_data:
            if self.validate_item(item):
                fields = [item[i] for i in self.indices]
                self.planes.append(Plane(*fields))
        return self.planes
