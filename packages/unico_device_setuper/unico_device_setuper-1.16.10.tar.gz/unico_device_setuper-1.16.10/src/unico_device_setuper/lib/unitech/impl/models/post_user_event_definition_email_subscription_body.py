from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostUserEventDefinitionEmailSubscriptionBody")


@_attrs_define
class PostUserEventDefinitionEmailSubscriptionBody:
    """
    Attributes:
        id_unitech_user (Union[Unset, Any]):  Example: any.
        ids_event_definition (Union[Unset, Any]):  Example: any.
    """

    id_unitech_user: Union[Unset, Any] = UNSET
    ids_event_definition: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id_unitech_user = self.id_unitech_user

        ids_event_definition = self.ids_event_definition

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id_unitech_user is not UNSET:
            field_dict["idUnitechUser"] = id_unitech_user
        if ids_event_definition is not UNSET:
            field_dict["idsEventDefinition"] = ids_event_definition

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id_unitech_user = d.pop("idUnitechUser", UNSET)

        ids_event_definition = d.pop("idsEventDefinition", UNSET)

        post_user_event_definition_email_subscription_body = cls(
            id_unitech_user=id_unitech_user,
            ids_event_definition=ids_event_definition,
        )

        post_user_event_definition_email_subscription_body.additional_properties = d
        return post_user_event_definition_email_subscription_body

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
