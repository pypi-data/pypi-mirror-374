from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostWasteBatchBody")


@_attrs_define
class PostWasteBatchBody:
    """
    Attributes:
        label (Union[Unset, Any]):  Example: any.
        outlet_id (Union[Unset, Any]):  Example: any.
        stream_id (Union[Unset, Any]):  Example: any.
    """

    label: Union[Unset, Any] = UNSET
    outlet_id: Union[Unset, Any] = UNSET
    stream_id: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        label = self.label

        outlet_id = self.outlet_id

        stream_id = self.stream_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if label is not UNSET:
            field_dict["label"] = label
        if outlet_id is not UNSET:
            field_dict["outletId"] = outlet_id
        if stream_id is not UNSET:
            field_dict["streamId"] = stream_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        label = d.pop("label", UNSET)

        outlet_id = d.pop("outletId", UNSET)

        stream_id = d.pop("streamId", UNSET)

        post_waste_batch_body = cls(
            label=label,
            outlet_id=outlet_id,
            stream_id=stream_id,
        )

        post_waste_batch_body.additional_properties = d
        return post_waste_batch_body

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
