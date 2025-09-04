from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutProducingPlaceRealisedIdBody")


@_attrs_define
class PutProducingPlaceRealisedIdBody:
    """
    Attributes:
        containers (Union[Unset, Any]):  Example: any.
        status (Union[Unset, Any]):  Example: any.
        comment (Union[Unset, Any]):  Example: any.
    """

    containers: Union[Unset, Any] = UNSET
    status: Union[Unset, Any] = UNSET
    comment: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        containers = self.containers

        status = self.status

        comment = self.comment

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if containers is not UNSET:
            field_dict["containers"] = containers
        if status is not UNSET:
            field_dict["status"] = status
        if comment is not UNSET:
            field_dict["comment"] = comment

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        containers = d.pop("containers", UNSET)

        status = d.pop("status", UNSET)

        comment = d.pop("comment", UNSET)

        put_producing_place_realised_id_body = cls(
            containers=containers,
            status=status,
            comment=comment,
        )

        put_producing_place_realised_id_body.additional_properties = d
        return put_producing_place_realised_id_body

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
