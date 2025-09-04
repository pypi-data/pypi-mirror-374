from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.author import Author


T = TypeVar("T", bound="CreatedPackage")


@_attrs_define
class CreatedPackage:
    """
    Attributes:
        name (str):
        label (str):
        disabled (bool):
        created (Author):
        updated (Union['Author', None, Unset]):
    """

    name: str
    label: str
    disabled: bool
    created: "Author"
    updated: Union["Author", None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.author import Author

        name = self.name

        label = self.label

        disabled = self.disabled

        created = self.created.to_dict()

        updated: Union[Dict[str, Any], None, Unset]
        if isinstance(self.updated, Unset):
            updated = UNSET
        elif isinstance(self.updated, Author):
            updated = self.updated.to_dict()
        else:
            updated = self.updated

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "label": label,
                "disabled": disabled,
                "created": created,
            }
        )
        if updated is not UNSET:
            field_dict["updated"] = updated

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.author import Author

        d = src_dict.copy()
        name = d.pop("name")

        label = d.pop("label")

        disabled = d.pop("disabled")

        created = Author.from_dict(d.pop("created"))

        def _parse_updated(data: object) -> Union["Author", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                updated_type_0 = Author.from_dict(data)

                return updated_type_0
            except:  # noqa: E722
                pass
            return cast(Union["Author", None, Unset], data)

        updated = _parse_updated(d.pop("updated", UNSET))

        created_package = cls(
            name=name,
            label=label,
            disabled=disabled,
            created=created,
            updated=updated,
        )

        created_package.additional_properties = d
        return created_package

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
