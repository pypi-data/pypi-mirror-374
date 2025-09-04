from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutEmployeeIdConstraintBody")


@_attrs_define
class PutEmployeeIdConstraintBody:
    """
    Attributes:
        interphone (Union[Unset, Any]):  Example: any.
        stairs (Union[Unset, Any]):  Example: any.
        slope (Union[Unset, Any]):  Example: any.
    """

    interphone: Union[Unset, Any] = UNSET
    stairs: Union[Unset, Any] = UNSET
    slope: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        interphone = self.interphone

        stairs = self.stairs

        slope = self.slope

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if interphone is not UNSET:
            field_dict["interphone"] = interphone
        if stairs is not UNSET:
            field_dict["stairs"] = stairs
        if slope is not UNSET:
            field_dict["slope"] = slope

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        interphone = d.pop("interphone", UNSET)

        stairs = d.pop("stairs", UNSET)

        slope = d.pop("slope", UNSET)

        put_employee_id_constraint_body = cls(
            interphone=interphone,
            stairs=stairs,
            slope=slope,
        )

        put_employee_id_constraint_body.additional_properties = d
        return put_employee_id_constraint_body

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
