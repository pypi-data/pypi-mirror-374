from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="RegisterDeviceResponse")


@_attrs_define
class RegisterDeviceResponse:
    """
    Attributes:
        id (str):  Example: string.
        name (str):  Example: string.
        id_device (str):  Example: string.
        id_client (str):  Example: string.
    """

    id: str
    name: str
    id_device: str
    id_client: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        id_device = self.id_device

        id_client = self.id_client

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "id_device": id_device,
                "id_client": id_client,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        id_device = d.pop("id_device")

        id_client = d.pop("id_client")

        register_device_response = cls(
            id=id,
            name=name,
            id_device=id_device,
            id_client=id_client,
        )

        register_device_response.additional_properties = d
        return register_device_response

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
