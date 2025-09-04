from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_pois_response_item_place import GetPoisResponseItemPlace
    from ..models.get_pois_response_item_poi_definition import GetPoisResponseItemPoiDefinition


T = TypeVar("T", bound="GetPoisResponseItem")


@_attrs_define
class GetPoisResponseItem:
    """
    Attributes:
        id (str):  Example: id.
        poi_definition (GetPoisResponseItemPoiDefinition):
        label (Union[Unset, str]):  Example: string.
        place (Union[Unset, GetPoisResponseItemPlace]):
    """

    id: str
    poi_definition: "GetPoisResponseItemPoiDefinition"
    label: Union[Unset, str] = UNSET
    place: Union[Unset, "GetPoisResponseItemPlace"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        poi_definition = self.poi_definition.to_dict()

        label = self.label

        place: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.place, Unset):
            place = self.place.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "poiDefinition": poi_definition,
            }
        )
        if label is not UNSET:
            field_dict["label"] = label
        if place is not UNSET:
            field_dict["place"] = place

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_pois_response_item_place import GetPoisResponseItemPlace
        from ..models.get_pois_response_item_poi_definition import GetPoisResponseItemPoiDefinition

        d = dict(src_dict)
        id = d.pop("id")

        poi_definition = GetPoisResponseItemPoiDefinition.from_dict(d.pop("poiDefinition"))

        label = d.pop("label", UNSET)

        _place = d.pop("place", UNSET)
        place: Union[Unset, GetPoisResponseItemPlace]
        if isinstance(_place, Unset):
            place = UNSET
        else:
            place = GetPoisResponseItemPlace.from_dict(_place)

        get_pois_response_item = cls(
            id=id,
            poi_definition=poi_definition,
            label=label,
            place=place,
        )

        get_pois_response_item.additional_properties = d
        return get_pois_response_item

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
