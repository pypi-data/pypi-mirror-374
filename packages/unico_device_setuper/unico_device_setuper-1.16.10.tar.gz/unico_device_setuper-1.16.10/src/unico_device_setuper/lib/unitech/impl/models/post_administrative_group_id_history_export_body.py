from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostAdministrativeGroupIdHistoryExportBody")


@_attrs_define
class PostAdministrativeGroupIdHistoryExportBody:
    """
    Attributes:
        start_date (Union[Unset, Any]):  Example: any.
        end_date (Union[Unset, Any]):  Example: any.
    """

    start_date: Union[Unset, Any] = UNSET
    end_date: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        start_date = self.start_date

        end_date = self.end_date

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if start_date is not UNSET:
            field_dict["startDate"] = start_date
        if end_date is not UNSET:
            field_dict["endDate"] = end_date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        start_date = d.pop("startDate", UNSET)

        end_date = d.pop("endDate", UNSET)

        post_administrative_group_id_history_export_body = cls(
            start_date=start_date,
            end_date=end_date,
        )

        post_administrative_group_id_history_export_body.additional_properties = d
        return post_administrative_group_id_history_export_body

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
