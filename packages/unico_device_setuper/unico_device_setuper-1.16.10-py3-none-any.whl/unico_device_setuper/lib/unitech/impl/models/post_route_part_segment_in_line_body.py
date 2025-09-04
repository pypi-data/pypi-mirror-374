from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostRoutePartSegmentInLineBody")


@_attrs_define
class PostRoutePartSegmentInLineBody:
    """
    Attributes:
        drawn_line (Union[Unset, Any]):  Example: any.
        mode (Union[Unset, Any]):  Example: any.
    """

    drawn_line: Union[Unset, Any] = UNSET
    mode: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        drawn_line = self.drawn_line

        mode = self.mode

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if drawn_line is not UNSET:
            field_dict["drawnLine"] = drawn_line
        if mode is not UNSET:
            field_dict["mode"] = mode

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        drawn_line = d.pop("drawnLine", UNSET)

        mode = d.pop("mode", UNSET)

        post_route_part_segment_in_line_body = cls(
            drawn_line=drawn_line,
            mode=mode,
        )

        post_route_part_segment_in_line_body.additional_properties = d
        return post_route_part_segment_in_line_body

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
