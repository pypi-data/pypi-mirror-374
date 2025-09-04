from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.poi_route_part import PoiRoutePart
    from ..models.segment_route_part import SegmentRoutePart


T = TypeVar("T", bound="ItineraryCreationData")


@_attrs_define
class ItineraryCreationData:
    """
    Attributes:
        distance_in_km (float):
        duration_in_ms (float):
        route_parts (list[Union['PoiRoutePart', 'SegmentRoutePart']]):
        round_instructions (list[Any]):
    """

    distance_in_km: float
    duration_in_ms: float
    route_parts: list[Union["PoiRoutePart", "SegmentRoutePart"]]
    round_instructions: list[Any]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.poi_route_part import PoiRoutePart

        distance_in_km = self.distance_in_km

        duration_in_ms = self.duration_in_ms

        route_parts = []
        for route_parts_item_data in self.route_parts:
            route_parts_item: dict[str, Any]
            if isinstance(route_parts_item_data, PoiRoutePart):
                route_parts_item = route_parts_item_data.to_dict()
            else:
                route_parts_item = route_parts_item_data.to_dict()

            route_parts.append(route_parts_item)

        round_instructions = self.round_instructions

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "distanceInKm": distance_in_km,
                "durationInMs": duration_in_ms,
                "routeParts": route_parts,
                "roundInstructions": round_instructions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.poi_route_part import PoiRoutePart
        from ..models.segment_route_part import SegmentRoutePart

        d = dict(src_dict)
        distance_in_km = d.pop("distanceInKm")

        duration_in_ms = d.pop("durationInMs")

        route_parts = []
        _route_parts = d.pop("routeParts")
        for route_parts_item_data in _route_parts:

            def _parse_route_parts_item(data: object) -> Union["PoiRoutePart", "SegmentRoutePart"]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_route_part_type_0 = PoiRoutePart.from_dict(data)

                    return componentsschemas_route_part_type_0
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_route_part_type_1 = SegmentRoutePart.from_dict(data)

                return componentsschemas_route_part_type_1

            route_parts_item = _parse_route_parts_item(route_parts_item_data)

            route_parts.append(route_parts_item)

        round_instructions = cast(list[Any], d.pop("roundInstructions"))

        itinerary_creation_data = cls(
            distance_in_km=distance_in_km,
            duration_in_ms=duration_in_ms,
            route_parts=route_parts,
            round_instructions=round_instructions,
        )

        itinerary_creation_data.additional_properties = d
        return itinerary_creation_data

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
