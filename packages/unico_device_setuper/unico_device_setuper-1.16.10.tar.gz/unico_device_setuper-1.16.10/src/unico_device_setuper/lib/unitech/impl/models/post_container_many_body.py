from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostContainerManyBody")


@_attrs_define
class PostContainerManyBody:
    """
    Attributes:
        should_use_stock (Union[Unset, Any]):  Example: any.
        id_assign_to (Union[Unset, Any]):  Example: any.
        containers_data (Union[Unset, Any]):  Example: any.
        depot_ids (Union[Unset, Any]):  Example: any.
    """

    should_use_stock: Union[Unset, Any] = UNSET
    id_assign_to: Union[Unset, Any] = UNSET
    containers_data: Union[Unset, Any] = UNSET
    depot_ids: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        should_use_stock = self.should_use_stock

        id_assign_to = self.id_assign_to

        containers_data = self.containers_data

        depot_ids = self.depot_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if should_use_stock is not UNSET:
            field_dict["shouldUseStock"] = should_use_stock
        if id_assign_to is not UNSET:
            field_dict["idAssignTo"] = id_assign_to
        if containers_data is not UNSET:
            field_dict["containersData"] = containers_data
        if depot_ids is not UNSET:
            field_dict["depotIds"] = depot_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        should_use_stock = d.pop("shouldUseStock", UNSET)

        id_assign_to = d.pop("idAssignTo", UNSET)

        containers_data = d.pop("containersData", UNSET)

        depot_ids = d.pop("depotIds", UNSET)

        post_container_many_body = cls(
            should_use_stock=should_use_stock,
            id_assign_to=id_assign_to,
            containers_data=containers_data,
            depot_ids=depot_ids,
        )

        post_container_many_body.additional_properties = d
        return post_container_many_body

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
