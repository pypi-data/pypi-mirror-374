from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostStreetServiceTransposeBody")


@_attrs_define
class PostStreetServiceTransposeBody:
    """
    Attributes:
        round_ (Union[Unset, Any]):  Example: any.
        realisation (Union[Unset, Any]):  Example: any.
        speed_on_segment_km_h (Union[Unset, Any]):  Example: any.
    """

    round_: Union[Unset, Any] = UNSET
    realisation: Union[Unset, Any] = UNSET
    speed_on_segment_km_h: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        round_ = self.round_

        realisation = self.realisation

        speed_on_segment_km_h = self.speed_on_segment_km_h

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if round_ is not UNSET:
            field_dict["round"] = round_
        if realisation is not UNSET:
            field_dict["realisation"] = realisation
        if speed_on_segment_km_h is not UNSET:
            field_dict["speedOnSegmentKmH"] = speed_on_segment_km_h

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        round_ = d.pop("round", UNSET)

        realisation = d.pop("realisation", UNSET)

        speed_on_segment_km_h = d.pop("speedOnSegmentKmH", UNSET)

        post_street_service_transpose_body = cls(
            round_=round_,
            realisation=realisation,
            speed_on_segment_km_h=speed_on_segment_km_h,
        )

        post_street_service_transpose_body.additional_properties = d
        return post_street_service_transpose_body

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
