from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostMapCorrectionBody")


@_attrs_define
class PostMapCorrectionBody:
    """
    Attributes:
        direction (Union[Unset, Any]):  Example: any.
        id_segment (Union[Unset, Any]):  Example: any.
    """

    direction: Union[Unset, Any] = UNSET
    id_segment: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        direction = self.direction

        id_segment = self.id_segment

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if direction is not UNSET:
            field_dict["direction"] = direction
        if id_segment is not UNSET:
            field_dict["idSegment"] = id_segment

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        direction = d.pop("direction", UNSET)

        id_segment = d.pop("idSegment", UNSET)

        post_map_correction_body = cls(
            direction=direction,
            id_segment=id_segment,
        )

        post_map_correction_body.additional_properties = d
        return post_map_correction_body

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
