from enum import Enum


class SegmentRoutePartSide(str, Enum):
    BOTH = "both"
    LEFT = "left"
    RIGHT = "right"

    def __str__(self) -> str:
        return str(self.value)
