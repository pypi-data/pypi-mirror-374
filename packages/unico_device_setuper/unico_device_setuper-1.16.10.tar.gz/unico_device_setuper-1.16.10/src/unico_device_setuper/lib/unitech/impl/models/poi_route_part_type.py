from enum import Enum


class PoiRoutePartType(str, Enum):
    DEPOT = "depot"
    EVENT = "event"
    INTERVENTION = "intervention"
    OUTLET = "outlet"
    POINTOFINTEREST = "pointOfInterest"
    PRODUCINGPLACE = "producingPlace"

    def __str__(self) -> str:
        return str(self.value)
