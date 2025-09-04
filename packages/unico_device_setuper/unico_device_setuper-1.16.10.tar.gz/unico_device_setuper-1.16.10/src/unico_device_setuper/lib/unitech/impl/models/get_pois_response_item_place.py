from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetPoisResponseItemPlace")


@_attrs_define
class GetPoisResponseItemPlace:
    """
    Attributes:
        longitude (float):
        latitude (float):
        city (Union[Unset, str]):  Example: string.
        postal_code (Union[Unset, str]):  Example: string.
        address (Union[Unset, str]):  Example: string.
    """

    longitude: float
    latitude: float
    city: Union[Unset, str] = UNSET
    postal_code: Union[Unset, str] = UNSET
    address: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        longitude = self.longitude

        latitude = self.latitude

        city = self.city

        postal_code = self.postal_code

        address = self.address

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "longitude": longitude,
                "latitude": latitude,
            }
        )
        if city is not UNSET:
            field_dict["city"] = city
        if postal_code is not UNSET:
            field_dict["postalCode"] = postal_code
        if address is not UNSET:
            field_dict["address"] = address

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        longitude = d.pop("longitude")

        latitude = d.pop("latitude")

        city = d.pop("city", UNSET)

        postal_code = d.pop("postalCode", UNSET)

        address = d.pop("address", UNSET)

        get_pois_response_item_place = cls(
            longitude=longitude,
            latitude=latitude,
            city=city,
            postal_code=postal_code,
            address=address,
        )

        get_pois_response_item_place.additional_properties = d
        return get_pois_response_item_place

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
