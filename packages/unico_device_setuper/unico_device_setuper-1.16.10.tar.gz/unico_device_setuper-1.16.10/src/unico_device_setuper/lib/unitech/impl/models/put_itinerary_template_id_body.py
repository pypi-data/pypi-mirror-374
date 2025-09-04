from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutItineraryTemplateIdBody")


@_attrs_define
class PutItineraryTemplateIdBody:
    """
    Attributes:
        itinerary_payload (Union[Unset, Any]):  Example: any.
    """

    itinerary_payload: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        itinerary_payload = self.itinerary_payload

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if itinerary_payload is not UNSET:
            field_dict["itineraryPayload"] = itinerary_payload

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        itinerary_payload = d.pop("itineraryPayload", UNSET)

        put_itinerary_template_id_body = cls(
            itinerary_payload=itinerary_payload,
        )

        put_itinerary_template_id_body.additional_properties = d
        return put_itinerary_template_id_body

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
