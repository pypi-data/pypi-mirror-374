from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.packages_model_packages import PackagesModelPackages


T = TypeVar("T", bound="PackagesModel")


@_attrs_define
class PackagesModel:
    """
    Attributes:
        packages (Union[Unset, PackagesModelPackages]):
    """

    packages: Union[Unset, "PackagesModelPackages"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        packages: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.packages, Unset):
            packages = self.packages.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if packages is not UNSET:
            field_dict["packages"] = packages

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.packages_model_packages import PackagesModelPackages

        d = src_dict.copy()
        _packages = d.pop("packages", UNSET)
        packages: Union[Unset, PackagesModelPackages]
        if isinstance(_packages, Unset):
            packages = UNSET
        else:
            packages = PackagesModelPackages.from_dict(_packages)

        packages_model = cls(
            packages=packages,
        )

        packages_model.additional_properties = d
        return packages_model

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
