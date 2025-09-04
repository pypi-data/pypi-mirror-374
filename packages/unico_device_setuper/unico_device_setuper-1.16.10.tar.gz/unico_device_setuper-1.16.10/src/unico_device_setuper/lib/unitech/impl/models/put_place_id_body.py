from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutPlaceIdBody")


@_attrs_define
class PutPlaceIdBody:
    """
    Attributes:
        latitude (Union[Unset, Any]):  Example: any.
        longitude (Union[Unset, Any]):  Example: any.
        address (Union[Unset, Any]):  Example: any.
        postal_code (Union[Unset, Any]):  Example: any.
        city (Union[Unset, Any]):  Example: any.
    """

    latitude: Union[Unset, Any] = UNSET
    longitude: Union[Unset, Any] = UNSET
    address: Union[Unset, Any] = UNSET
    postal_code: Union[Unset, Any] = UNSET
    city: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        latitude = self.latitude

        longitude = self.longitude

        address = self.address

        postal_code = self.postal_code

        city = self.city

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if latitude is not UNSET:
            field_dict["latitude"] = latitude
        if longitude is not UNSET:
            field_dict["longitude"] = longitude
        if address is not UNSET:
            field_dict["address"] = address
        if postal_code is not UNSET:
            field_dict["postalCode"] = postal_code
        if city is not UNSET:
            field_dict["city"] = city

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        latitude = d.pop("latitude", UNSET)

        longitude = d.pop("longitude", UNSET)

        address = d.pop("address", UNSET)

        postal_code = d.pop("postalCode", UNSET)

        city = d.pop("city", UNSET)

        put_place_id_body = cls(
            latitude=latitude,
            longitude=longitude,
            address=address,
            postal_code=postal_code,
            city=city,
        )

        put_place_id_body.additional_properties = d
        return put_place_id_body

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
