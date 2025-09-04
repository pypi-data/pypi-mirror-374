from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutStreamIdBody")


@_attrs_define
class PutStreamIdBody:
    """
    Attributes:
        label (Union[Unset, Any]):  Example: any.
        color (Union[Unset, Any]):  Example: any.
        logo_url (Union[Unset, Any]):  Example: any.
        volumic_mass_kg_per_liter (Union[Unset, Any]):  Example: any.
        track_dechet_elimination_code (Union[Unset, Any]):  Example: any.
        track_dechet_waste_stream_id (Union[Unset, Any]):  Example: any.
    """

    label: Union[Unset, Any] = UNSET
    color: Union[Unset, Any] = UNSET
    logo_url: Union[Unset, Any] = UNSET
    volumic_mass_kg_per_liter: Union[Unset, Any] = UNSET
    track_dechet_elimination_code: Union[Unset, Any] = UNSET
    track_dechet_waste_stream_id: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        label = self.label

        color = self.color

        logo_url = self.logo_url

        volumic_mass_kg_per_liter = self.volumic_mass_kg_per_liter

        track_dechet_elimination_code = self.track_dechet_elimination_code

        track_dechet_waste_stream_id = self.track_dechet_waste_stream_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if label is not UNSET:
            field_dict["label"] = label
        if color is not UNSET:
            field_dict["color"] = color
        if logo_url is not UNSET:
            field_dict["logoUrl"] = logo_url
        if volumic_mass_kg_per_liter is not UNSET:
            field_dict["volumicMassKgPerLiter"] = volumic_mass_kg_per_liter
        if track_dechet_elimination_code is not UNSET:
            field_dict["trackDechetEliminationCode"] = track_dechet_elimination_code
        if track_dechet_waste_stream_id is not UNSET:
            field_dict["trackDechetWasteStreamId"] = track_dechet_waste_stream_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        label = d.pop("label", UNSET)

        color = d.pop("color", UNSET)

        logo_url = d.pop("logoUrl", UNSET)

        volumic_mass_kg_per_liter = d.pop("volumicMassKgPerLiter", UNSET)

        track_dechet_elimination_code = d.pop("trackDechetEliminationCode", UNSET)

        track_dechet_waste_stream_id = d.pop("trackDechetWasteStreamId", UNSET)

        put_stream_id_body = cls(
            label=label,
            color=color,
            logo_url=logo_url,
            volumic_mass_kg_per_liter=volumic_mass_kg_per_liter,
            track_dechet_elimination_code=track_dechet_elimination_code,
            track_dechet_waste_stream_id=track_dechet_waste_stream_id,
        )

        put_stream_id_body.additional_properties = d
        return put_stream_id_body

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
