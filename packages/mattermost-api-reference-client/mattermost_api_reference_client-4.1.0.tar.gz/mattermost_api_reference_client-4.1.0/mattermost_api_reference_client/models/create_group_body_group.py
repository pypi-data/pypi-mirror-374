from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CreateGroupBodyGroup")


@_attrs_define
class CreateGroupBodyGroup:
    """Group object to create.

    Attributes:
        name (str): The unique group name used for at-mentioning.
        display_name (str): The display name of the group which can include spaces.
        source (str): Must be `custom`
        allow_reference (bool): Must be true
    """

    name: str
    display_name: str
    source: str
    allow_reference: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        display_name = self.display_name

        source = self.source

        allow_reference = self.allow_reference

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "display_name": display_name,
                "source": source,
                "allow_reference": allow_reference,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        display_name = d.pop("display_name")

        source = d.pop("source")

        allow_reference = d.pop("allow_reference")

        create_group_body_group = cls(
            name=name,
            display_name=display_name,
            source=source,
            allow_reference=allow_reference,
        )

        create_group_body_group.additional_properties = d
        return create_group_body_group

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
