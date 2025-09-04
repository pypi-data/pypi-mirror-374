from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutEventDefinitionIdBody")


@_attrs_define
class PutEventDefinitionIdBody:
    """
    Attributes:
        label (Union[Unset, Any]):  Example: any.
        type_ (Union[Unset, Any]):  Example: any.
        logo_url (Union[Unset, Any]):  Example: any.
        is_comment_required (Union[Unset, Any]):  Example: any.
        is_signature_required (Union[Unset, Any]):  Example: any.
        is_picture_required (Union[Unset, Any]):  Example: any.
        id_event_definition_category (Union[Unset, Any]):  Example: any.
        initial_state (Union[Unset, Any]):  Example: any.
        is_visible_on_uniandco (Union[Unset, Any]):  Example: any.
        intervention_duration_sec (Union[Unset, Any]):  Example: any.
        can_be_created_on_uninav (Union[Unset, Any]):  Example: any.
        archived_at (Union[Unset, Any]):  Example: any.
    """

    label: Union[Unset, Any] = UNSET
    type_: Union[Unset, Any] = UNSET
    logo_url: Union[Unset, Any] = UNSET
    is_comment_required: Union[Unset, Any] = UNSET
    is_signature_required: Union[Unset, Any] = UNSET
    is_picture_required: Union[Unset, Any] = UNSET
    id_event_definition_category: Union[Unset, Any] = UNSET
    initial_state: Union[Unset, Any] = UNSET
    is_visible_on_uniandco: Union[Unset, Any] = UNSET
    intervention_duration_sec: Union[Unset, Any] = UNSET
    can_be_created_on_uninav: Union[Unset, Any] = UNSET
    archived_at: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        label = self.label

        type_ = self.type_

        logo_url = self.logo_url

        is_comment_required = self.is_comment_required

        is_signature_required = self.is_signature_required

        is_picture_required = self.is_picture_required

        id_event_definition_category = self.id_event_definition_category

        initial_state = self.initial_state

        is_visible_on_uniandco = self.is_visible_on_uniandco

        intervention_duration_sec = self.intervention_duration_sec

        can_be_created_on_uninav = self.can_be_created_on_uninav

        archived_at = self.archived_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if label is not UNSET:
            field_dict["label"] = label
        if type_ is not UNSET:
            field_dict["type"] = type_
        if logo_url is not UNSET:
            field_dict["logoUrl"] = logo_url
        if is_comment_required is not UNSET:
            field_dict["isCommentRequired"] = is_comment_required
        if is_signature_required is not UNSET:
            field_dict["isSignatureRequired"] = is_signature_required
        if is_picture_required is not UNSET:
            field_dict["isPictureRequired"] = is_picture_required
        if id_event_definition_category is not UNSET:
            field_dict["idEventDefinitionCategory"] = id_event_definition_category
        if initial_state is not UNSET:
            field_dict["initialState"] = initial_state
        if is_visible_on_uniandco is not UNSET:
            field_dict["isVisibleOnUniandco"] = is_visible_on_uniandco
        if intervention_duration_sec is not UNSET:
            field_dict["interventionDurationSec"] = intervention_duration_sec
        if can_be_created_on_uninav is not UNSET:
            field_dict["canBeCreatedOnUninav"] = can_be_created_on_uninav
        if archived_at is not UNSET:
            field_dict["archivedAt"] = archived_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        label = d.pop("label", UNSET)

        type_ = d.pop("type", UNSET)

        logo_url = d.pop("logoUrl", UNSET)

        is_comment_required = d.pop("isCommentRequired", UNSET)

        is_signature_required = d.pop("isSignatureRequired", UNSET)

        is_picture_required = d.pop("isPictureRequired", UNSET)

        id_event_definition_category = d.pop("idEventDefinitionCategory", UNSET)

        initial_state = d.pop("initialState", UNSET)

        is_visible_on_uniandco = d.pop("isVisibleOnUniandco", UNSET)

        intervention_duration_sec = d.pop("interventionDurationSec", UNSET)

        can_be_created_on_uninav = d.pop("canBeCreatedOnUninav", UNSET)

        archived_at = d.pop("archivedAt", UNSET)

        put_event_definition_id_body = cls(
            label=label,
            type_=type_,
            logo_url=logo_url,
            is_comment_required=is_comment_required,
            is_signature_required=is_signature_required,
            is_picture_required=is_picture_required,
            id_event_definition_category=id_event_definition_category,
            initial_state=initial_state,
            is_visible_on_uniandco=is_visible_on_uniandco,
            intervention_duration_sec=intervention_duration_sec,
            can_be_created_on_uninav=can_be_created_on_uninav,
            archived_at=archived_at,
        )

        put_event_definition_id_body.additional_properties = d
        return put_event_definition_id_body

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
