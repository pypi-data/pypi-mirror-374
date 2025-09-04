from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostExternalCreateIFMItineraryIdRealisationBody")


@_attrs_define
class PostExternalCreateIFMItineraryIdRealisationBody:
    """
    Attributes:
        date_realised (Union[Unset, Any]):  Example: any.
    """

    date_realised: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        date_realised = self.date_realised

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if date_realised is not UNSET:
            field_dict["dateRealised"] = date_realised

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        date_realised = d.pop("dateRealised", UNSET)

        post_external_create_ifm_itinerary_id_realisation_body = cls(
            date_realised=date_realised,
        )

        post_external_create_ifm_itinerary_id_realisation_body.additional_properties = d
        return post_external_create_ifm_itinerary_id_realisation_body

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
