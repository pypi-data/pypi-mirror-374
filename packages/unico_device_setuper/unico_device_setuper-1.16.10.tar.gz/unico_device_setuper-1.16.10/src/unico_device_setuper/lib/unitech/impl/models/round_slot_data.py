from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.round_slot_data_recurrence_type import RoundSlotDataRecurrenceType
from ..types import UNSET, Unset

T = TypeVar("T", bound="RoundSlotData")


@_attrs_define
class RoundSlotData:
    """
    Attributes:
        activation_date (str):  Example: date.
        time_start (str):  Example: date.
        recurrence_type (RoundSlotDataRecurrenceType):
        occurrence_in_period (float):
        deactivation_date (Union[Unset, str]):  Example: date.
        recurrence_period (Union[Unset, float]):
    """

    activation_date: str
    time_start: str
    recurrence_type: RoundSlotDataRecurrenceType
    occurrence_in_period: float
    deactivation_date: Union[Unset, str] = UNSET
    recurrence_period: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        activation_date = self.activation_date

        time_start = self.time_start

        recurrence_type = self.recurrence_type.value

        occurrence_in_period = self.occurrence_in_period

        deactivation_date = self.deactivation_date

        recurrence_period = self.recurrence_period

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "activationDate": activation_date,
                "timeStart": time_start,
                "recurrenceType": recurrence_type,
                "occurrenceInPeriod": occurrence_in_period,
            }
        )
        if deactivation_date is not UNSET:
            field_dict["deactivationDate"] = deactivation_date
        if recurrence_period is not UNSET:
            field_dict["recurrencePeriod"] = recurrence_period

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        activation_date = d.pop("activationDate")

        time_start = d.pop("timeStart")

        recurrence_type = RoundSlotDataRecurrenceType(d.pop("recurrenceType"))

        occurrence_in_period = d.pop("occurrenceInPeriod")

        deactivation_date = d.pop("deactivationDate", UNSET)

        recurrence_period = d.pop("recurrencePeriod", UNSET)

        round_slot_data = cls(
            activation_date=activation_date,
            time_start=time_start,
            recurrence_type=recurrence_type,
            occurrence_in_period=occurrence_in_period,
            deactivation_date=deactivation_date,
            recurrence_period=recurrence_period,
        )

        round_slot_data.additional_properties = d
        return round_slot_data

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
