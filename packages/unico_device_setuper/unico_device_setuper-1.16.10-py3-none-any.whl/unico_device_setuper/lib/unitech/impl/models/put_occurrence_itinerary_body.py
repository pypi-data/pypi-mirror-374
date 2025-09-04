from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutOccurrenceItineraryBody")


@_attrs_define
class PutOccurrenceItineraryBody:
    """
    Attributes:
        id_round_slot (Union[Unset, Any]):  Example: any.
        recurrence_num (Union[Unset, Any]):  Example: any.
    """

    id_round_slot: Union[Unset, Any] = UNSET
    recurrence_num: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id_round_slot = self.id_round_slot

        recurrence_num = self.recurrence_num

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id_round_slot is not UNSET:
            field_dict["idRoundSlot"] = id_round_slot
        if recurrence_num is not UNSET:
            field_dict["recurrenceNum"] = recurrence_num

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id_round_slot = d.pop("idRoundSlot", UNSET)

        recurrence_num = d.pop("recurrenceNum", UNSET)

        put_occurrence_itinerary_body = cls(
            id_round_slot=id_round_slot,
            recurrence_num=recurrence_num,
        )

        put_occurrence_itinerary_body.additional_properties = d
        return put_occurrence_itinerary_body

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
