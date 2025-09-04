from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutUserPreferencesLogisticParamsColumnBody")


@_attrs_define
class PutUserPreferencesLogisticParamsColumnBody:
    """
    Attributes:
        id_column (Union[Unset, Any]):  Example: any.
        is_visible (Union[Unset, Any]):  Example: any.
    """

    id_column: Union[Unset, Any] = UNSET
    is_visible: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id_column = self.id_column

        is_visible = self.is_visible

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id_column is not UNSET:
            field_dict["idColumn"] = id_column
        if is_visible is not UNSET:
            field_dict["isVisible"] = is_visible

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id_column = d.pop("idColumn", UNSET)

        is_visible = d.pop("isVisible", UNSET)

        put_user_preferences_logistic_params_column_body = cls(
            id_column=id_column,
            is_visible=is_visible,
        )

        put_user_preferences_logistic_params_column_body.additional_properties = d
        return put_user_preferences_logistic_params_column_body

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
