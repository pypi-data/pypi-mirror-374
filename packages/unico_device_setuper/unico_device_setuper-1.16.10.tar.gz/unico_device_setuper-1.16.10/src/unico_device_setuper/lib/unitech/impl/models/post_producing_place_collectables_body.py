from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostProducingPlaceCollectablesBody")


@_attrs_define
class PostProducingPlaceCollectablesBody:
    """
    Attributes:
        sector_ids (Union[Unset, Any]):  Example: any.
    """

    sector_ids: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        sector_ids = self.sector_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if sector_ids is not UNSET:
            field_dict["sectorIds"] = sector_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        sector_ids = d.pop("sectorIds", UNSET)

        post_producing_place_collectables_body = cls(
            sector_ids=sector_ids,
        )

        post_producing_place_collectables_body.additional_properties = d
        return post_producing_place_collectables_body

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
