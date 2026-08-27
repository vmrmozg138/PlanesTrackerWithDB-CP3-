from functools import total_ordering


@total_ordering
class Plane:
    def __init__(
        self,
        planeID: str,
        callsign: str,
        reg_country: str,
        height: float,
        onground: bool,
        speed: float,
    ):
        self.__planeID = planeID
        self.__callsign = callsign
        self.__reg_country = reg_country
        self.__height = height
        self.__onground = onground
        self.__speed = speed

    def to_dict(self) -> dict:
        return {
            "planeID": self.__planeID,
            "callsign": self.__callsign,
            "reg_country": self.__reg_country,
            "height": self.__height,
            "onground": self.__onground,
            "speed": self.__speed,
        }

    def __eq__(self, other):
        return self.__speed == other.__speed

    def __lt__(self, other):
        return self.__speed < other.__speed

    def __gt__(self, other):
        return self.__speed > other.__speed

    def __ge__(self, other):
        return self.__speed >= other.__speed

    def __le__(self, other):
        return self.__speed <= other.__speed

    def __ne__(self, other):
        return self.__speed != other.__speed

    def is_higher_than(self, other):
        return self.__height > other.__height

    def is_lower_than(self, other):
        return self.__height < other.__height
