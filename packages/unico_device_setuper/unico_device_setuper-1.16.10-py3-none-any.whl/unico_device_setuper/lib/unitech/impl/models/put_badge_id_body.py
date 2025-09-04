from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutBadgeIdBody")


@_attrs_define
class PutBadgeIdBody:
    """
    Attributes:
        expires_at (Union[Unset, Any]):  Example: any.
        is_active (Union[Unset, Any]):  Example: any.
        last_use_datetime (Union[Unset, Any]):  Example: any.
        reference (Union[Unset, Any]):  Example: any.
        administrative_group (Union[Unset, Any]):  Example: any.
        description (Union[Unset, Any]):  Example: any.
    """

    expires_at: Union[Unset, Any] = UNSET
    is_active: Union[Unset, Any] = UNSET
    last_use_datetime: Union[Unset, Any] = UNSET
    reference: Union[Unset, Any] = UNSET
    administrative_group: Union[Unset, Any] = UNSET
    description: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        expires_at = self.expires_at

        is_active = self.is_active

        last_use_datetime = self.last_use_datetime

        reference = self.reference

        administrative_group = self.administrative_group

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if expires_at is not UNSET:
            field_dict["expiresAt"] = expires_at
        if is_active is not UNSET:
            field_dict["isActive"] = is_active
        if last_use_datetime is not UNSET:
            field_dict["lastUseDatetime"] = last_use_datetime
        if reference is not UNSET:
            field_dict["reference"] = reference
        if administrative_group is not UNSET:
            field_dict["administrativeGroup"] = administrative_group
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        expires_at = d.pop("expiresAt", UNSET)

        is_active = d.pop("isActive", UNSET)

        last_use_datetime = d.pop("lastUseDatetime", UNSET)

        reference = d.pop("reference", UNSET)

        administrative_group = d.pop("administrativeGroup", UNSET)

        description = d.pop("description", UNSET)

        put_badge_id_body = cls(
            expires_at=expires_at,
            is_active=is_active,
            last_use_datetime=last_use_datetime,
            reference=reference,
            administrative_group=administrative_group,
            description=description,
        )

        put_badge_id_body.additional_properties = d
        return put_badge_id_body

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
