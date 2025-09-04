from enum import Enum


class SegmentRoutePartInterventionMode(str, Enum):
    BACKWARD = "backward"
    ON_FOOT = "on_foot"
    REGULAR = "regular"

    def __str__(self) -> str:
        return str(self.value)
