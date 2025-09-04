from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostRoutePartAvailabilitiesBody")


@_attrs_define
class PostRoutePartAvailabilitiesBody:
    """
    Attributes:
        days (Union[Unset, Any]):  Example: any.
        producing_place_ids (Union[Unset, Any]):  Example: any.
    """

    days: Union[Unset, Any] = UNSET
    producing_place_ids: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        days = self.days

        producing_place_ids = self.producing_place_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if days is not UNSET:
            field_dict["days"] = days
        if producing_place_ids is not UNSET:
            field_dict["producingPlaceIds"] = producing_place_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        days = d.pop("days", UNSET)

        producing_place_ids = d.pop("producingPlaceIds", UNSET)

        post_route_part_availabilities_body = cls(
            days=days,
            producing_place_ids=producing_place_ids,
        )

        post_route_part_availabilities_body.additional_properties = d
        return post_route_part_availabilities_body

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
