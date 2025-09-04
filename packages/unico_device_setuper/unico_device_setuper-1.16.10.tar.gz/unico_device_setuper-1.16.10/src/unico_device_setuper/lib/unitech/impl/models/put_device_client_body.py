from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutDeviceClientBody")


@_attrs_define
class PutDeviceClientBody:
    """
    Attributes:
        go_to_next_automatic (Union[Unset, Any]):  Example: any.
    """

    go_to_next_automatic: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        go_to_next_automatic = self.go_to_next_automatic

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if go_to_next_automatic is not UNSET:
            field_dict["goToNextAutomatic"] = go_to_next_automatic

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        go_to_next_automatic = d.pop("goToNextAutomatic", UNSET)

        put_device_client_body = cls(
            go_to_next_automatic=go_to_next_automatic,
        )

        put_device_client_body.additional_properties = d
        return put_device_client_body

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
