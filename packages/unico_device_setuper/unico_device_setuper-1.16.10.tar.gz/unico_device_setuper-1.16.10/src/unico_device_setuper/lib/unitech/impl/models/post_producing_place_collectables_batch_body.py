from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostProducingPlaceCollectablesBatchBody")


@_attrs_define
class PostProducingPlaceCollectablesBatchBody:
    """
    Attributes:
        order (Union[Unset, Any]):  Example: any.
        filters (Union[Unset, Any]):  Example: any.
        page (Union[Unset, Any]):  Example: any.
    """

    order: Union[Unset, Any] = UNSET
    filters: Union[Unset, Any] = UNSET
    page: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        order = self.order

        filters = self.filters

        page = self.page

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if order is not UNSET:
            field_dict["order"] = order
        if filters is not UNSET:
            field_dict["filters"] = filters
        if page is not UNSET:
            field_dict["page"] = page

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        order = d.pop("order", UNSET)

        filters = d.pop("filters", UNSET)

        page = d.pop("page", UNSET)

        post_producing_place_collectables_batch_body = cls(
            order=order,
            filters=filters,
            page=page,
        )

        post_producing_place_collectables_batch_body.additional_properties = d
        return post_producing_place_collectables_batch_body

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
