from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutEmployeeIdBody")


@_attrs_define
class PutEmployeeIdBody:
    """
    Attributes:
        contract (Union[Unset, Any]):  Example: any.
        start_of_contract (Union[Unset, Any]):  Example: any.
        end_of_contract (Union[Unset, Any]):  Example: any.
        reference (Union[Unset, Any]):  Example: any.
        archivation_datetime (Union[Unset, Any]):  Example: any.
        sectors (Union[Unset, Any]):  Example: any.
        jobs (Union[Unset, Any]):  Example: any.
        firstname (Union[Unset, Any]):  Example: any.
        lastname (Union[Unset, Any]):  Example: any.
        email (Union[Unset, Any]):  Example: any.
        phone (Union[Unset, Any]):  Example: any.
    """

    contract: Union[Unset, Any] = UNSET
    start_of_contract: Union[Unset, Any] = UNSET
    end_of_contract: Union[Unset, Any] = UNSET
    reference: Union[Unset, Any] = UNSET
    archivation_datetime: Union[Unset, Any] = UNSET
    sectors: Union[Unset, Any] = UNSET
    jobs: Union[Unset, Any] = UNSET
    firstname: Union[Unset, Any] = UNSET
    lastname: Union[Unset, Any] = UNSET
    email: Union[Unset, Any] = UNSET
    phone: Union[Unset, Any] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        contract = self.contract

        start_of_contract = self.start_of_contract

        end_of_contract = self.end_of_contract

        reference = self.reference

        archivation_datetime = self.archivation_datetime

        sectors = self.sectors

        jobs = self.jobs

        firstname = self.firstname

        lastname = self.lastname

        email = self.email

        phone = self.phone

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if contract is not UNSET:
            field_dict["contract"] = contract
        if start_of_contract is not UNSET:
            field_dict["startOfContract"] = start_of_contract
        if end_of_contract is not UNSET:
            field_dict["endOfContract"] = end_of_contract
        if reference is not UNSET:
            field_dict["reference"] = reference
        if archivation_datetime is not UNSET:
            field_dict["archivationDatetime"] = archivation_datetime
        if sectors is not UNSET:
            field_dict["sectors"] = sectors
        if jobs is not UNSET:
            field_dict["jobs"] = jobs
        if firstname is not UNSET:
            field_dict["firstname"] = firstname
        if lastname is not UNSET:
            field_dict["lastname"] = lastname
        if email is not UNSET:
            field_dict["email"] = email
        if phone is not UNSET:
            field_dict["phone"] = phone

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        contract = d.pop("contract", UNSET)

        start_of_contract = d.pop("startOfContract", UNSET)

        end_of_contract = d.pop("endOfContract", UNSET)

        reference = d.pop("reference", UNSET)

        archivation_datetime = d.pop("archivationDatetime", UNSET)

        sectors = d.pop("sectors", UNSET)

        jobs = d.pop("jobs", UNSET)

        firstname = d.pop("firstname", UNSET)

        lastname = d.pop("lastname", UNSET)

        email = d.pop("email", UNSET)

        phone = d.pop("phone", UNSET)

        put_employee_id_body = cls(
            contract=contract,
            start_of_contract=start_of_contract,
            end_of_contract=end_of_contract,
            reference=reference,
            archivation_datetime=archivation_datetime,
            sectors=sectors,
            jobs=jobs,
            firstname=firstname,
            lastname=lastname,
            email=email,
            phone=phone,
        )

        put_employee_id_body.additional_properties = d
        return put_employee_id_body

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
