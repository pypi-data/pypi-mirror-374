from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CurrentUserResponse")


@_attrs_define
class CurrentUserResponse:
    """
    Attributes:
        username (str):  Example: string.
        lastname (str):  Example: string.
        firstname (str):  Example: string.
    """

    username: str
    lastname: str
    firstname: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        username = self.username

        lastname = self.lastname

        firstname = self.firstname

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "username": username,
                "lastname": lastname,
                "firstname": firstname,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        username = d.pop("username")

        lastname = d.pop("lastname")

        firstname = d.pop("firstname")

        current_user_response = cls(
            username=username,
            lastname=lastname,
            firstname=firstname,
        )

        current_user_response.additional_properties = d
        return current_user_response

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
