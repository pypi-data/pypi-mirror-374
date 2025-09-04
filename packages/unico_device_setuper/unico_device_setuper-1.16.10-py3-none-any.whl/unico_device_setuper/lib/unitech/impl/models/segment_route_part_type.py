from enum import Enum


class SegmentRoutePartType(str, Enum):
    SEGMENT = "segment"

    def __str__(self) -> str:
        return str(self.value)
