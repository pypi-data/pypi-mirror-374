from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.round_creation_data_type import RoundCreationDataType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.itinerary_creation_data import ItineraryCreationData
    from ..models.round_slot_data import RoundSlotData


T = TypeVar("T", bound="RoundCreationData")


@_attrs_define
class RoundCreationData:
    """
    Attributes:
        label (str):  Example: string.
        stream_labels (list[str]):  Example: ['string'].
        sector_ids (list[str]):  Example: ['id'].
        operator_ids (list[str]):  Example: ['id'].
        type_ (RoundCreationDataType):
        start_date (str):  Example: date.
        itinerary_planified (ItineraryCreationData):
        round_slots (list['RoundSlotData']):
        id_depot (str):  Example: id.
        id_outlet (str):  Example: id.
        id_driver (Union[Unset, str]):  Example: id.
        id_vehicle (Union[Unset, str]):  Example: id.
    """

    label: str
    stream_labels: list[str]
    sector_ids: list[str]
    operator_ids: list[str]
    type_: RoundCreationDataType
    start_date: str
    itinerary_planified: "ItineraryCreationData"
    round_slots: list["RoundSlotData"]
    id_depot: str
    id_outlet: str
    id_driver: Union[Unset, str] = UNSET
    id_vehicle: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        label = self.label

        stream_labels = self.stream_labels

        sector_ids = self.sector_ids

        operator_ids = self.operator_ids

        type_ = self.type_.value

        start_date = self.start_date

        itinerary_planified = self.itinerary_planified.to_dict()

        round_slots = []
        for round_slots_item_data in self.round_slots:
            round_slots_item = round_slots_item_data.to_dict()
            round_slots.append(round_slots_item)

        id_depot = self.id_depot

        id_outlet = self.id_outlet

        id_driver = self.id_driver

        id_vehicle = self.id_vehicle

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "label": label,
                "streamLabels": stream_labels,
                "sectorIds": sector_ids,
                "operatorIds": operator_ids,
                "type": type_,
                "startDate": start_date,
                "itineraryPlanified": itinerary_planified,
                "roundSlots": round_slots,
                "idDepot": id_depot,
                "idOutlet": id_outlet,
            }
        )
        if id_driver is not UNSET:
            field_dict["idDriver"] = id_driver
        if id_vehicle is not UNSET:
            field_dict["idVehicle"] = id_vehicle

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.itinerary_creation_data import ItineraryCreationData
        from ..models.round_slot_data import RoundSlotData

        d = dict(src_dict)
        label = d.pop("label")

        stream_labels = cast(list[str], d.pop("streamLabels"))

        sector_ids = cast(list[str], d.pop("sectorIds"))

        operator_ids = cast(list[str], d.pop("operatorIds"))

        type_ = RoundCreationDataType(d.pop("type"))

        start_date = d.pop("startDate")

        itinerary_planified = ItineraryCreationData.from_dict(d.pop("itineraryPlanified"))

        round_slots = []
        _round_slots = d.pop("roundSlots")
        for round_slots_item_data in _round_slots:
            round_slots_item = RoundSlotData.from_dict(round_slots_item_data)

            round_slots.append(round_slots_item)

        id_depot = d.pop("idDepot")

        id_outlet = d.pop("idOutlet")

        id_driver = d.pop("idDriver", UNSET)

        id_vehicle = d.pop("idVehicle", UNSET)

        round_creation_data = cls(
            label=label,
            stream_labels=stream_labels,
            sector_ids=sector_ids,
            operator_ids=operator_ids,
            type_=type_,
            start_date=start_date,
            itinerary_planified=itinerary_planified,
            round_slots=round_slots,
            id_depot=id_depot,
            id_outlet=id_outlet,
            id_driver=id_driver,
            id_vehicle=id_vehicle,
        )

        round_creation_data.additional_properties = d
        return round_creation_data

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
