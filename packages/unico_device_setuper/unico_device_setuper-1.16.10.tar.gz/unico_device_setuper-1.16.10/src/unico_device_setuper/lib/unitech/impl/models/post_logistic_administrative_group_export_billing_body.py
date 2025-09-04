from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostLogisticAdministrativeGroupExportBillingBody")


@_attrs_define
class PostLogisticAdministrativeGroupExportBillingBody:
    """
    Attributes:
        date_range (Union[Unset, Any]):  Example: any.
    """

    date_range: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        date_range = self.date_range

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if date_range is not UNSET:
            field_dict["dateRange"] = date_range

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        date_range = d.pop("dateRange", UNSET)

        post_logistic_administrative_group_export_billing_body = cls(
            date_range=date_range,
        )

        post_logistic_administrative_group_export_billing_body.additional_properties = d
        return post_logistic_administrative_group_export_billing_body

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
