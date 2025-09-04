from enum import Enum


class RoundCreationDataType(str, Enum):
    BULKYREMOVALS = "bulkyRemovals"
    MULTISTREAM = "multiStream"
    UNIQUESTREAM = "uniqueStream"

    def __str__(self) -> str:
        return str(self.value)
