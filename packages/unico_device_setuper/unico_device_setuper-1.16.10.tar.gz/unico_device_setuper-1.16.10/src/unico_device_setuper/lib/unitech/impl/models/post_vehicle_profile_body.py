from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostVehicleProfileBody")


@_attrs_define
class PostVehicleProfileBody:
    """
    Attributes:
        label (Union[Unset, Any]):  Example: any.
        height_mm (Union[Unset, Any]):  Example: any.
        length_mm (Union[Unset, Any]):  Example: any.
        width_mm (Union[Unset, Any]):  Example: any.
        axle_weight_kg (Union[Unset, Any]):  Example: any.
        weight_kg (Union[Unset, Any]):  Example: any.
        maximum_speed_km_per_hour (Union[Unset, Any]):  Example: any.
        volume (Union[Unset, Any]):  Example: any.
        floor_area (Union[Unset, Any]):  Example: any.
        type_ (Union[Unset, Any]):  Example: any.
    """

    label: Union[Unset, Any] = UNSET
    height_mm: Union[Unset, Any] = UNSET
    length_mm: Union[Unset, Any] = UNSET
    width_mm: Union[Unset, Any] = UNSET
    axle_weight_kg: Union[Unset, Any] = UNSET
    weight_kg: Union[Unset, Any] = UNSET
    maximum_speed_km_per_hour: Union[Unset, Any] = UNSET
    volume: Union[Unset, Any] = UNSET
    floor_area: Union[Unset, Any] = UNSET
    type_: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        label = self.label

        height_mm = self.height_mm

        length_mm = self.length_mm

        width_mm = self.width_mm

        axle_weight_kg = self.axle_weight_kg

        weight_kg = self.weight_kg

        maximum_speed_km_per_hour = self.maximum_speed_km_per_hour

        volume = self.volume

        floor_area = self.floor_area

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if label is not UNSET:
            field_dict["label"] = label
        if height_mm is not UNSET:
            field_dict["heightMm"] = height_mm
        if length_mm is not UNSET:
            field_dict["lengthMm"] = length_mm
        if width_mm is not UNSET:
            field_dict["widthMm"] = width_mm
        if axle_weight_kg is not UNSET:
            field_dict["axleWeightKg"] = axle_weight_kg
        if weight_kg is not UNSET:
            field_dict["weightKg"] = weight_kg
        if maximum_speed_km_per_hour is not UNSET:
            field_dict["maximumSpeedKmPerHour"] = maximum_speed_km_per_hour
        if volume is not UNSET:
            field_dict["volume"] = volume
        if floor_area is not UNSET:
            field_dict["floorArea"] = floor_area
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        label = d.pop("label", UNSET)

        height_mm = d.pop("heightMm", UNSET)

        length_mm = d.pop("lengthMm", UNSET)

        width_mm = d.pop("widthMm", UNSET)

        axle_weight_kg = d.pop("axleWeightKg", UNSET)

        weight_kg = d.pop("weightKg", UNSET)

        maximum_speed_km_per_hour = d.pop("maximumSpeedKmPerHour", UNSET)

        volume = d.pop("volume", UNSET)

        floor_area = d.pop("floorArea", UNSET)

        type_ = d.pop("type", UNSET)

        post_vehicle_profile_body = cls(
            label=label,
            height_mm=height_mm,
            length_mm=length_mm,
            width_mm=width_mm,
            axle_weight_kg=axle_weight_kg,
            weight_kg=weight_kg,
            maximum_speed_km_per_hour=maximum_speed_km_per_hour,
            volume=volume,
            floor_area=floor_area,
            type_=type_,
        )

        post_vehicle_profile_body.additional_properties = d
        return post_vehicle_profile_body

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
