from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostDeviceSubmitCheckInBody")


@_attrs_define
class PostDeviceSubmitCheckInBody:
    """
    Attributes:
        answers (Union[Unset, Any]):  Example: any.
        submit_date_time (Union[Unset, Any]):  Example: any.
        id_round_realisation (Union[Unset, Any]):  Example: any.
    """

    answers: Union[Unset, Any] = UNSET
    submit_date_time: Union[Unset, Any] = UNSET
    id_round_realisation: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        answers = self.answers

        submit_date_time = self.submit_date_time

        id_round_realisation = self.id_round_realisation

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if answers is not UNSET:
            field_dict["answers"] = answers
        if submit_date_time is not UNSET:
            field_dict["submitDateTime"] = submit_date_time
        if id_round_realisation is not UNSET:
            field_dict["idRoundRealisation"] = id_round_realisation

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        answers = d.pop("answers", UNSET)

        submit_date_time = d.pop("submitDateTime", UNSET)

        id_round_realisation = d.pop("idRoundRealisation", UNSET)

        post_device_submit_check_in_body = cls(
            answers=answers,
            submit_date_time=submit_date_time,
            id_round_realisation=id_round_realisation,
        )

        post_device_submit_check_in_body.additional_properties = d
        return post_device_submit_check_in_body

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
