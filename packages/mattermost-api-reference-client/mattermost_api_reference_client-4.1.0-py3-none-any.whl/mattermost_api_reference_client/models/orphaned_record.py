from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OrphanedRecord")


@_attrs_define
class OrphanedRecord:
    """an object containing information about an orphaned record.

    Attributes:
        parent_id (Union[Unset, str]): the id of the parent relation (table) entry.
        child_id (Union[Unset, str]): the id of the child relation (table) entry.
    """

    parent_id: Union[Unset, str] = UNSET
    child_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        parent_id = self.parent_id

        child_id = self.child_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if parent_id is not UNSET:
            field_dict["parent_id"] = parent_id
        if child_id is not UNSET:
            field_dict["child_id"] = child_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        parent_id = d.pop("parent_id", UNSET)

        child_id = d.pop("child_id", UNSET)

        orphaned_record = cls(
            parent_id=parent_id,
            child_id=child_id,
        )

        orphaned_record.additional_properties = d
        return orphaned_record

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
