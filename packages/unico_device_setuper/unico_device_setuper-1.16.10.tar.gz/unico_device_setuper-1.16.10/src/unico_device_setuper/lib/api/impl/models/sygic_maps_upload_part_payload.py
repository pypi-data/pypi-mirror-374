from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="SygicMapsUploadPartPayload")


@_attrs_define
class SygicMapsUploadPartPayload:
    """
    Attributes:
        content (str):
        num (int):
        upload_id (str):
    """

    content: str
    num: int
    upload_id: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        content = self.content

        num = self.num

        upload_id = self.upload_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "content": content,
                "num": num,
                "upload_id": upload_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        content = d.pop("content")

        num = d.pop("num")

        upload_id = d.pop("upload_id")

        sygic_maps_upload_part_payload = cls(
            content=content,
            num=num,
            upload_id=upload_id,
        )

        sygic_maps_upload_part_payload.additional_properties = d
        return sygic_maps_upload_part_payload

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
