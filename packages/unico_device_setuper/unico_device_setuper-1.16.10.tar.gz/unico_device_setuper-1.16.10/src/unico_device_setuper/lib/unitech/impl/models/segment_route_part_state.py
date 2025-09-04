from enum import Enum


class SegmentRoutePartState(str, Enum):
    INVALIDATED = "invalidated"
    VALIDATED = "validated"
    VISITED = "visited"

    def __str__(self) -> str:
        return str(self.value)
