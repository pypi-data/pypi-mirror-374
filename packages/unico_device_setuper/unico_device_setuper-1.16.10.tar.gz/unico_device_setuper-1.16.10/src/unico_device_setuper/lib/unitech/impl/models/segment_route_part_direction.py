from enum import Enum


class SegmentRoutePartDirection(str, Enum):
    FORWARD = "forward"
    REVERSE = "reverse"

    def __str__(self) -> str:
        return str(self.value)
