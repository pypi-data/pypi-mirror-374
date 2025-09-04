from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostUserBody")


@_attrs_define
class PostUserBody:
    """
    Attributes:
        email (Union[Unset, Any]):  Example: any.
        firstname (Union[Unset, Any]):  Example: any.
        lastname (Union[Unset, Any]):  Example: any.
        permissions (Union[Unset, Any]):  Example: any.
        role (Union[Unset, Any]):  Example: any.
        sectors (Union[Unset, Any]):  Example: any.
    """

    email: Union[Unset, Any] = UNSET
    firstname: Union[Unset, Any] = UNSET
    lastname: Union[Unset, Any] = UNSET
    permissions: Union[Unset, Any] = UNSET
    role: Union[Unset, Any] = UNSET
    sectors: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        firstname = self.firstname

        lastname = self.lastname

        permissions = self.permissions

        role = self.role

        sectors = self.sectors

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if email is not UNSET:
            field_dict["email"] = email
        if firstname is not UNSET:
            field_dict["firstname"] = firstname
        if lastname is not UNSET:
            field_dict["lastname"] = lastname
        if permissions is not UNSET:
            field_dict["permissions"] = permissions
        if role is not UNSET:
            field_dict["role"] = role
        if sectors is not UNSET:
            field_dict["sectors"] = sectors

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email", UNSET)

        firstname = d.pop("firstname", UNSET)

        lastname = d.pop("lastname", UNSET)

        permissions = d.pop("permissions", UNSET)

        role = d.pop("role", UNSET)

        sectors = d.pop("sectors", UNSET)

        post_user_body = cls(
            email=email,
            firstname=firstname,
            lastname=lastname,
            permissions=permissions,
            role=role,
            sectors=sectors,
        )

        post_user_body.additional_properties = d
        return post_user_body

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
