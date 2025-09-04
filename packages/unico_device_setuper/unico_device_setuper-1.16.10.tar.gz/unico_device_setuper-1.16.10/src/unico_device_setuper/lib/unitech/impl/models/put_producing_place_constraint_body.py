from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutProducingPlaceConstraintBody")


@_attrs_define
class PutProducingPlaceConstraintBody:
    """
    Attributes:
        id (Union[Unset, Any]):  Example: any.
        vehicles (Union[Unset, Any]):  Example: any.
        id_producing_place (Union[Unset, Any]):  Example: any.
    """

    id: Union[Unset, Any] = UNSET
    vehicles: Union[Unset, Any] = UNSET
    id_producing_place: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        vehicles = self.vehicles

        id_producing_place = self.id_producing_place

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if vehicles is not UNSET:
            field_dict["vehicles"] = vehicles
        if id_producing_place is not UNSET:
            field_dict["idProducingPlace"] = id_producing_place

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        vehicles = d.pop("vehicles", UNSET)

        id_producing_place = d.pop("idProducingPlace", UNSET)

        put_producing_place_constraint_body = cls(
            id=id,
            vehicles=vehicles,
            id_producing_place=id_producing_place,
        )

        put_producing_place_constraint_body.additional_properties = d
        return put_producing_place_constraint_body

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
