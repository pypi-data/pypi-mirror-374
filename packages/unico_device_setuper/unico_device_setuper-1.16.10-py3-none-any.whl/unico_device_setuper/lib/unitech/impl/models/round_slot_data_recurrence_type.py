from enum import Enum


class RoundSlotDataRecurrenceType(str, Enum):
    UNIQUE = "unique"
    WEEK = "week"

    def __str__(self) -> str:
        return str(self.value)
