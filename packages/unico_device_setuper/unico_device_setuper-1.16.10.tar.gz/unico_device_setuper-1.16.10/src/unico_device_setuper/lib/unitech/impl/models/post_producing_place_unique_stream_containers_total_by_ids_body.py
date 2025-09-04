from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostProducingPlaceUniqueStreamContainersTotalByIdsBody")


@_attrs_define
class PostProducingPlaceUniqueStreamContainersTotalByIdsBody:
    """
    Attributes:
        producing_place_ids (Union[Unset, Any]):  Example: any.
        stream_label (Union[Unset, Any]):  Example: any.
    """

    producing_place_ids: Union[Unset, Any] = UNSET
    stream_label: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        producing_place_ids = self.producing_place_ids

        stream_label = self.stream_label

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if producing_place_ids is not UNSET:
            field_dict["producingPlaceIds"] = producing_place_ids
        if stream_label is not UNSET:
            field_dict["streamLabel"] = stream_label

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        producing_place_ids = d.pop("producingPlaceIds", UNSET)

        stream_label = d.pop("streamLabel", UNSET)

        post_producing_place_unique_stream_containers_total_by_ids_body = cls(
            producing_place_ids=producing_place_ids,
            stream_label=stream_label,
        )

        post_producing_place_unique_stream_containers_total_by_ids_body.additional_properties = d
        return post_producing_place_unique_stream_containers_total_by_ids_body

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
