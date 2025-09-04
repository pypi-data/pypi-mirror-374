from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostRotationHistoryBody")


@_attrs_define
class PostRotationHistoryBody:
    """
    Attributes:
        container_id (Union[Unset, Any]):  Example: any.
        type_ (Union[Unset, Any]):  Example: any.
        depot_id (Union[Unset, Any]):  Example: any.
        producing_place_id (Union[Unset, Any]):  Example: any.
        round_realisation_id (Union[Unset, Any]):  Example: any.
        date (Union[Unset, Any]):  Example: any.
    """

    container_id: Union[Unset, Any] = UNSET
    type_: Union[Unset, Any] = UNSET
    depot_id: Union[Unset, Any] = UNSET
    producing_place_id: Union[Unset, Any] = UNSET
    round_realisation_id: Union[Unset, Any] = UNSET
    date: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        container_id = self.container_id

        type_ = self.type_

        depot_id = self.depot_id

        producing_place_id = self.producing_place_id

        round_realisation_id = self.round_realisation_id

        date = self.date

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if container_id is not UNSET:
            field_dict["containerId"] = container_id
        if type_ is not UNSET:
            field_dict["type"] = type_
        if depot_id is not UNSET:
            field_dict["depotId"] = depot_id
        if producing_place_id is not UNSET:
            field_dict["producingPlaceId"] = producing_place_id
        if round_realisation_id is not UNSET:
            field_dict["roundRealisationId"] = round_realisation_id
        if date is not UNSET:
            field_dict["date"] = date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        container_id = d.pop("containerId", UNSET)

        type_ = d.pop("type", UNSET)

        depot_id = d.pop("depotId", UNSET)

        producing_place_id = d.pop("producingPlaceId", UNSET)

        round_realisation_id = d.pop("roundRealisationId", UNSET)

        date = d.pop("date", UNSET)

        post_rotation_history_body = cls(
            container_id=container_id,
            type_=type_,
            depot_id=depot_id,
            producing_place_id=producing_place_id,
            round_realisation_id=round_realisation_id,
            date=date,
        )

        post_rotation_history_body.additional_properties = d
        return post_rotation_history_body

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
