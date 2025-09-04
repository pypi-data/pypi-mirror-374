from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ChangelogResponse")


@_attrs_define
class ChangelogResponse:
    """
    Attributes:
        latest_version_name (str):  Example: string.
        latest_version_code (float):
        release_url (str):  Example: string.
    """

    latest_version_name: str
    latest_version_code: float
    release_url: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        latest_version_name = self.latest_version_name

        latest_version_code = self.latest_version_code

        release_url = self.release_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "latestVersionName": latest_version_name,
                "latestVersionCode": latest_version_code,
                "releaseUrl": release_url,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        latest_version_name = d.pop("latestVersionName")

        latest_version_code = d.pop("latestVersionCode")

        release_url = d.pop("releaseUrl")

        changelog_response = cls(
            latest_version_name=latest_version_name,
            latest_version_code=latest_version_code,
            release_url=release_url,
        )

        changelog_response.additional_properties = d
        return changelog_response

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
