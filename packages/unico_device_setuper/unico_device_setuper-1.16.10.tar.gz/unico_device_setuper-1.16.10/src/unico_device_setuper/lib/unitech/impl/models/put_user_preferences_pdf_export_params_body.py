from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutUserPreferencesPdfExportParamsBody")


@_attrs_define
class PutUserPreferencesPdfExportParamsBody:
    """
    Attributes:
        show_deadheading (Union[Unset, Any]):  Example: any.
        show_depot_outlet (Union[Unset, Any]):  Example: any.
    """

    show_deadheading: Union[Unset, Any] = UNSET
    show_depot_outlet: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        show_deadheading = self.show_deadheading

        show_depot_outlet = self.show_depot_outlet

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if show_deadheading is not UNSET:
            field_dict["showDeadheading"] = show_deadheading
        if show_depot_outlet is not UNSET:
            field_dict["showDepotOutlet"] = show_depot_outlet

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        show_deadheading = d.pop("showDeadheading", UNSET)

        show_depot_outlet = d.pop("showDepotOutlet", UNSET)

        put_user_preferences_pdf_export_params_body = cls(
            show_deadheading=show_deadheading,
            show_depot_outlet=show_depot_outlet,
        )

        put_user_preferences_pdf_export_params_body.additional_properties = d
        return put_user_preferences_pdf_export_params_body

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
