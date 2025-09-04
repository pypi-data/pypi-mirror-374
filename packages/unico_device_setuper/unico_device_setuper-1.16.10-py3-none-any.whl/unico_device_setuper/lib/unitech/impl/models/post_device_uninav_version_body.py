from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostDeviceUninavVersionBody")


@_attrs_define
class PostDeviceUninavVersionBody:
    """
    Attributes:
        version_code (Union[Unset, Any]):  Example: any.
        version_name (Union[Unset, Any]):  Example: any.
        release_url (Union[Unset, Any]):  Example: any.
    """

    version_code: Union[Unset, Any] = UNSET
    version_name: Union[Unset, Any] = UNSET
    release_url: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        version_code = self.version_code

        version_name = self.version_name

        release_url = self.release_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if version_code is not UNSET:
            field_dict["versionCode"] = version_code
        if version_name is not UNSET:
            field_dict["versionName"] = version_name
        if release_url is not UNSET:
            field_dict["releaseUrl"] = release_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        version_code = d.pop("versionCode", UNSET)

        version_name = d.pop("versionName", UNSET)

        release_url = d.pop("releaseUrl", UNSET)

        post_device_uninav_version_body = cls(
            version_code=version_code,
            version_name=version_name,
            release_url=release_url,
        )

        post_device_uninav_version_body.additional_properties = d
        return post_device_uninav_version_body

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
