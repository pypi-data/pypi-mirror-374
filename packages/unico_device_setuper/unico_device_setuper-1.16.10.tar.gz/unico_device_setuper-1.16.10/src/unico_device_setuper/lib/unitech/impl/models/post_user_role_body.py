from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostUserRoleBody")


@_attrs_define
class PostUserRoleBody:
    """
    Attributes:
        logistic (Union[Unset, Any]):  Example: any.
        label (Union[Unset, Any]):  Example: any.
        dashboard (Union[Unset, Any]):  Example: any.
        operational (Union[Unset, Any]):  Example: any.
        cartography (Union[Unset, Any]):  Example: any.
        planning (Union[Unset, Any]):  Example: any.
        tour_tracking (Union[Unset, Any]):  Example: any.
    """

    logistic: Union[Unset, Any] = UNSET
    label: Union[Unset, Any] = UNSET
    dashboard: Union[Unset, Any] = UNSET
    operational: Union[Unset, Any] = UNSET
    cartography: Union[Unset, Any] = UNSET
    planning: Union[Unset, Any] = UNSET
    tour_tracking: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        logistic = self.logistic

        label = self.label

        dashboard = self.dashboard

        operational = self.operational

        cartography = self.cartography

        planning = self.planning

        tour_tracking = self.tour_tracking

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if logistic is not UNSET:
            field_dict["logistic"] = logistic
        if label is not UNSET:
            field_dict["label"] = label
        if dashboard is not UNSET:
            field_dict["dashboard"] = dashboard
        if operational is not UNSET:
            field_dict["operational"] = operational
        if cartography is not UNSET:
            field_dict["cartography"] = cartography
        if planning is not UNSET:
            field_dict["planning"] = planning
        if tour_tracking is not UNSET:
            field_dict["tourTracking"] = tour_tracking

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        logistic = d.pop("logistic", UNSET)

        label = d.pop("label", UNSET)

        dashboard = d.pop("dashboard", UNSET)

        operational = d.pop("operational", UNSET)

        cartography = d.pop("cartography", UNSET)

        planning = d.pop("planning", UNSET)

        tour_tracking = d.pop("tourTracking", UNSET)

        post_user_role_body = cls(
            logistic=logistic,
            label=label,
            dashboard=dashboard,
            operational=operational,
            cartography=cartography,
            planning=planning,
            tour_tracking=tour_tracking,
        )

        post_user_role_body.additional_properties = d
        return post_user_role_body

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
