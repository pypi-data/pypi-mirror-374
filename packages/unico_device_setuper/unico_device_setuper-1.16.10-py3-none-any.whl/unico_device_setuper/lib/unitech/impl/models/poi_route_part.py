from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.poi_route_part_state import PoiRoutePartState
from ..models.poi_route_part_type import PoiRoutePartType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.poi_route_part_producing_place import PoiRoutePartProducingPlace


T = TypeVar("T", bound="PoiRoutePart")


@_attrs_define
class PoiRoutePart:
    """
    Attributes:
        id (str):  Example: id.
        type_ (PoiRoutePartType):
        longitude (float):
        latitude (float):
        is_u_turn_allowed (bool):
        label (Union[Unset, str]):  Example: string.
        detail (Union[Unset, str]):  Example: string.
        is_order_locked (Union[Unset, bool]):
        city (Union[Unset, str]):  Example: string.
        arrival_time_estimation (Union[Unset, float]):
        travel_time_estimation (Union[Unset, float]):
        collect_time (Union[Unset, float]):
        is_realised (Union[Unset, bool]):
        state (Union[Unset, PoiRoutePartState]):
        id_poi (Union[Unset, str]):  Example: id.
        reference (Union[Unset, str]):  Example: string.
        serial_num (Union[Unset, str]):  Example: string.
        id_place (Union[Unset, str]):  Example: id.
        author (Union[Unset, str]):  Example: string.
        producing_place (Union[Unset, PoiRoutePartProducingPlace]):
        is_available (Union[Unset, bool]):
    """

    id: str
    type_: PoiRoutePartType
    longitude: float
    latitude: float
    is_u_turn_allowed: bool
    label: Union[Unset, str] = UNSET
    detail: Union[Unset, str] = UNSET
    is_order_locked: Union[Unset, bool] = UNSET
    city: Union[Unset, str] = UNSET
    arrival_time_estimation: Union[Unset, float] = UNSET
    travel_time_estimation: Union[Unset, float] = UNSET
    collect_time: Union[Unset, float] = UNSET
    is_realised: Union[Unset, bool] = UNSET
    state: Union[Unset, PoiRoutePartState] = UNSET
    id_poi: Union[Unset, str] = UNSET
    reference: Union[Unset, str] = UNSET
    serial_num: Union[Unset, str] = UNSET
    id_place: Union[Unset, str] = UNSET
    author: Union[Unset, str] = UNSET
    producing_place: Union[Unset, "PoiRoutePartProducingPlace"] = UNSET
    is_available: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        type_ = self.type_.value

        longitude = self.longitude

        latitude = self.latitude

        is_u_turn_allowed = self.is_u_turn_allowed

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

        id_poi = self.id_poi

        reference = self.reference

        serial_num = self.serial_num

        id_place = self.id_place

        author = self.author

        producing_place: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.producing_place, Unset):
            producing_place = self.producing_place.to_dict()

        is_available = self.is_available

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "type": type_,
                "longitude": longitude,
                "latitude": latitude,
                "isUTurnAllowed": is_u_turn_allowed,
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
        if id_poi is not UNSET:
            field_dict["idPoi"] = id_poi
        if reference is not UNSET:
            field_dict["reference"] = reference
        if serial_num is not UNSET:
            field_dict["serialNum"] = serial_num
        if id_place is not UNSET:
            field_dict["idPlace"] = id_place
        if author is not UNSET:
            field_dict["author"] = author
        if producing_place is not UNSET:
            field_dict["producingPlace"] = producing_place
        if is_available is not UNSET:
            field_dict["isAvailable"] = is_available

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.poi_route_part_producing_place import PoiRoutePartProducingPlace

        d = dict(src_dict)
        id = d.pop("id")

        type_ = PoiRoutePartType(d.pop("type"))

        longitude = d.pop("longitude")

        latitude = d.pop("latitude")

        is_u_turn_allowed = d.pop("isUTurnAllowed")

        label = d.pop("label", UNSET)

        detail = d.pop("detail", UNSET)

        is_order_locked = d.pop("isOrderLocked", UNSET)

        city = d.pop("city", UNSET)

        arrival_time_estimation = d.pop("arrivalTimeEstimation", UNSET)

        travel_time_estimation = d.pop("travelTimeEstimation", UNSET)

        collect_time = d.pop("collectTime", UNSET)

        is_realised = d.pop("isRealised", UNSET)

        _state = d.pop("state", UNSET)
        state: Union[Unset, PoiRoutePartState]
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = PoiRoutePartState(_state)

        id_poi = d.pop("idPoi", UNSET)

        reference = d.pop("reference", UNSET)

        serial_num = d.pop("serialNum", UNSET)

        id_place = d.pop("idPlace", UNSET)

        author = d.pop("author", UNSET)

        _producing_place = d.pop("producingPlace", UNSET)
        producing_place: Union[Unset, PoiRoutePartProducingPlace]
        if isinstance(_producing_place, Unset):
            producing_place = UNSET
        else:
            producing_place = PoiRoutePartProducingPlace.from_dict(_producing_place)

        is_available = d.pop("isAvailable", UNSET)

        poi_route_part = cls(
            id=id,
            type_=type_,
            longitude=longitude,
            latitude=latitude,
            is_u_turn_allowed=is_u_turn_allowed,
            label=label,
            detail=detail,
            is_order_locked=is_order_locked,
            city=city,
            arrival_time_estimation=arrival_time_estimation,
            travel_time_estimation=travel_time_estimation,
            collect_time=collect_time,
            is_realised=is_realised,
            state=state,
            id_poi=id_poi,
            reference=reference,
            serial_num=serial_num,
            id_place=id_place,
            author=author,
            producing_place=producing_place,
            is_available=is_available,
        )

        poi_route_part.additional_properties = d
        return poi_route_part

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
