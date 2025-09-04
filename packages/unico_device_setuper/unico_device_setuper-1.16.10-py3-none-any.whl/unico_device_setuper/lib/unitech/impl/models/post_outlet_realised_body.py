from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostOutletRealisedBody")


@_attrs_define
class PostOutletRealisedBody:
    """
    Attributes:
        round_realisation_id (Union[Unset, Any]):  Example: any.
    """

    round_realisation_id: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        round_realisation_id = self.round_realisation_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if round_realisation_id is not UNSET:
            field_dict["roundRealisationId"] = round_realisation_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        round_realisation_id = d.pop("roundRealisationId", UNSET)

        post_outlet_realised_body = cls(
            round_realisation_id=round_realisation_id,
        )

        post_outlet_realised_body.additional_properties = d
        return post_outlet_realised_body

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
