from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutRoutePartMoveManyBody")


@_attrs_define
class PutRoutePartMoveManyBody:
    """
    Attributes:
        occurrence_id (Union[Unset, Any]):  Example: any.
        moved_route_parts (Union[Unset, Any]):  Example: any.
    """

    occurrence_id: Union[Unset, Any] = UNSET
    moved_route_parts: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        occurrence_id = self.occurrence_id

        moved_route_parts = self.moved_route_parts

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if occurrence_id is not UNSET:
            field_dict["occurrenceId"] = occurrence_id
        if moved_route_parts is not UNSET:
            field_dict["movedRouteParts"] = moved_route_parts

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        occurrence_id = d.pop("occurrenceId", UNSET)

        moved_route_parts = d.pop("movedRouteParts", UNSET)

        put_route_part_move_many_body = cls(
            occurrence_id=occurrence_id,
            moved_route_parts=moved_route_parts,
        )

        put_route_part_move_many_body.additional_properties = d
        return put_route_part_move_many_body

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
