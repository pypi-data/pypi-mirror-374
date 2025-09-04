from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DeleteRoundIdRoundBody")


@_attrs_define
class DeleteRoundIdRoundBody:
    """
    Attributes:
        activation_datetime (Union[Unset, Any]):  Example: any.
        start_date (Union[Unset, Any]):  Example: any.
        id_round (Union[Unset, Any]):  Example: any.
        override_occurrences (Union[Unset, Any]):  Example: any.
        itinerary_planified (Union[Unset, Any]):  Example: any.
    """

    activation_datetime: Union[Unset, Any] = UNSET
    start_date: Union[Unset, Any] = UNSET
    id_round: Union[Unset, Any] = UNSET
    override_occurrences: Union[Unset, Any] = UNSET
    itinerary_planified: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        activation_datetime = self.activation_datetime

        start_date = self.start_date

        id_round = self.id_round

        override_occurrences = self.override_occurrences

        itinerary_planified = self.itinerary_planified

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if activation_datetime is not UNSET:
            field_dict["activationDatetime"] = activation_datetime
        if start_date is not UNSET:
            field_dict["startDate"] = start_date
        if id_round is not UNSET:
            field_dict["idRound"] = id_round
        if override_occurrences is not UNSET:
            field_dict["overrideOccurrences"] = override_occurrences
        if itinerary_planified is not UNSET:
            field_dict["itineraryPlanified"] = itinerary_planified

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        activation_datetime = d.pop("activationDatetime", UNSET)

        start_date = d.pop("startDate", UNSET)

        id_round = d.pop("idRound", UNSET)

        override_occurrences = d.pop("overrideOccurrences", UNSET)

        itinerary_planified = d.pop("itineraryPlanified", UNSET)

        delete_round_id_round_body = cls(
            activation_datetime=activation_datetime,
            start_date=start_date,
            id_round=id_round,
            override_occurrences=override_occurrences,
            itinerary_planified=itinerary_planified,
        )

        delete_round_id_round_body.additional_properties = d
        return delete_round_id_round_body

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
