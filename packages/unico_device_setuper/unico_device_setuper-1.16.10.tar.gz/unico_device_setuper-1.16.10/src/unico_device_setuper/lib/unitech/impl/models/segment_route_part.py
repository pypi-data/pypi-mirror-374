from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.segment_route_part_direction import SegmentRoutePartDirection
from ..models.segment_route_part_intervention_mode import SegmentRoutePartInterventionMode
from ..models.segment_route_part_side import SegmentRoutePartSide
from ..models.segment_route_part_state import SegmentRoutePartState
from ..models.segment_route_part_type import SegmentRoutePartType
from ..types import UNSET, Unset

T = TypeVar("T", bound="SegmentRoutePart")


@_attrs_define
class SegmentRoutePart:
    """
    Attributes:
        id (str):  Example: id.
        type_ (SegmentRoutePartType):
        id_segment (str):  Example: id.
        direction (SegmentRoutePartDirection):
        side (SegmentRoutePartSide):
        coordinates (list[list[float]]):
        should_intervene (bool):
        intervention_mode (SegmentRoutePartInterventionMode):
        is_one_way (bool):
        label (Union[Unset, str]):  Example: string.
        detail (Union[Unset, str]):  Example: string.
        is_order_locked (Union[Unset, bool]):
        city (Union[Unset, str]):  Example: string.
        arrival_time_estimation (Union[Unset, float]):
        travel_time_estimation (Union[Unset, float]):
        collect_time (Union[Unset, float]):
        is_realised (Union[Unset, bool]):
        state (Union[Unset, SegmentRoutePartState]):
        merged_with (Union[Unset, list[str]]):  Example: ['id'].
    """

    id: str
    type_: SegmentRoutePartType
    id_segment: str
    direction: SegmentRoutePartDirection
    side: SegmentRoutePartSide
    coordinates: list[list[float]]
    should_intervene: bool
    intervention_mode: SegmentRoutePartInterventionMode
    is_one_way: bool
    label: Union[Unset, str] = UNSET
    detail: Union[Unset, str] = UNSET
    is_order_locked: Union[Unset, bool] = UNSET
    city: Union[Unset, str] = UNSET
    arrival_time_estimation: Union[Unset, float] = UNSET
    travel_time_estimation: Union[Unset, float] = UNSET
    collect_time: Union[Unset, float] = UNSET
    is_realised: Union[Unset, bool] = UNSET
    state: Union[Unset, SegmentRoutePartState] = UNSET
    merged_with: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        type_ = self.type_.value

        id_segment = self.id_segment

        direction = self.direction.value

        side = self.side.value

        coordinates = []
        for coordinates_item_data in self.coordinates:
            coordinates_item = coordinates_item_data

            coordinates.append(coordinates_item)

        should_intervene = self.should_intervene

        intervention_mode = self.intervention_mode.value

        is_one_way = self.is_one_way

        label = self.label

        detail = self.detail

        is_order_locked = self.is_order_locked

        city = self.city

        arrival_time_estimation = self.arrival_time_estimation

        travel_time_estimation = self.travel_time_estimation

        collect_time = self.collect_time

        is_realised = self.is_realised

        state: Union[Unset, str] = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value

        merged_with: Union[Unset, list[str]] = UNSET
        if not isinstance(self.merged_with, Unset):
            merged_with = self.merged_with

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "type": type_,
                "idSegment": id_segment,
                "direction": direction,
                "side": side,
                "coordinates": coordinates,
                "shouldIntervene": should_intervene,
                "interventionMode": intervention_mode,
                "isOneWay": is_one_way,
            }
        )
        if label is not UNSET:
            field_dict["label"] = label
        if detail is not UNSET:
            field_dict["detail"] = detail
        if is_order_locked is not UNSET:
            field_dict["isOrderLocked"] = is_order_locked
        if city is not UNSET:
            field_dict["city"] = city
        if arrival_time_estimation is not UNSET:
            field_dict["arrivalTimeEstimation"] = arrival_time_estimation
        if travel_time_estimation is not UNSET:
            field_dict["travelTimeEstimation"] = travel_time_estimation
        if collect_time is not UNSET:
            field_dict["collectTime"] = collect_time
        if is_realised is not UNSET:
            field_dict["isRealised"] = is_realised
        if state is not UNSET:
            field_dict["state"] = state
        if merged_with is not UNSET:
            field_dict["mergedWith"] = merged_with

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        type_ = SegmentRoutePartType(d.pop("type"))

        id_segment = d.pop("idSegment")

        direction = SegmentRoutePartDirection(d.pop("direction"))

        side = SegmentRoutePartSide(d.pop("side"))

        coordinates = []
        _coordinates = d.pop("coordinates")
        for coordinates_item_data in _coordinates:
            coordinates_item = cast(list[float], coordinates_item_data)

            coordinates.append(coordinates_item)

        should_intervene = d.pop("shouldIntervene")

        intervention_mode = SegmentRoutePartInterventionMode(d.pop("interventionMode"))

        is_one_way = d.pop("isOneWay")

        label = d.pop("label", UNSET)

        detail = d.pop("detail", UNSET)

        is_order_locked = d.pop("isOrderLocked", UNSET)

        city = d.pop("city", UNSET)

        arrival_time_estimation = d.pop("arrivalTimeEstimation", UNSET)

        travel_time_estimation = d.pop("travelTimeEstimation", UNSET)

        collect_time = d.pop("collectTime", UNSET)

        is_realised = d.pop("isRealised", UNSET)

        _state = d.pop("state", UNSET)
        state: Union[Unset, SegmentRoutePartState]
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = SegmentRoutePartState(_state)

        merged_with = cast(list[str], d.pop("mergedWith", UNSET))

        segment_route_part = cls(
            id=id,
            type_=type_,
            id_segment=id_segment,
            direction=direction,
            side=side,
            coordinates=coordinates,
            should_intervene=should_intervene,
            intervention_mode=intervention_mode,
            is_one_way=is_one_way,
            label=label,
            detail=detail,
            is_order_locked=is_order_locked,
            city=city,
            arrival_time_estimation=arrival_time_estimation,
            travel_time_estimation=travel_time_estimation,
            collect_time=collect_time,
            is_realised=is_realised,
            state=state,
            merged_with=merged_with,
        )

        segment_route_part.additional_properties = d
        return segment_route_part

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
