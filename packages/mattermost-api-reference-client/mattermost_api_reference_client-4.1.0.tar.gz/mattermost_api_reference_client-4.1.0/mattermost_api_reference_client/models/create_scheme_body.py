from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateSchemeBody")


@_attrs_define
class CreateSchemeBody:
    """
    Attributes:
        display_name (str): The display name of the scheme
        scope (str): The scope of the scheme ("team" or "channel")
        name (Union[Unset, str]): The name of the scheme
        description (Union[Unset, str]): The description of the scheme
    """

    display_name: str
    scope: str
    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        display_name = self.display_name

        scope = self.scope

        name = self.name

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "display_name": display_name,
                "scope": scope,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        display_name = d.pop("display_name")

        scope = d.pop("scope")

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        create_scheme_body = cls(
            display_name=display_name,
            scope=scope,
            name=name,
            description=description,
        )

        create_scheme_body.additional_properties = d
        return create_scheme_body

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
