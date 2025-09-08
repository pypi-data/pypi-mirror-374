from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ItemSetAssigneeBody")


@_attrs_define
class ItemSetAssigneeBody:
    """
    Attributes:
        assignee_id (str): The user ID of the new assignee of the item. Example: ruu86intseidqdxjojia41u7l1.
    """

    assignee_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        assignee_id = self.assignee_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "assignee_id": assignee_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        assignee_id = d.pop("assignee_id")

        item_set_assignee_body = cls(
            assignee_id=assignee_id,
        )

        item_set_assignee_body.additional_properties = d
        return item_set_assignee_body

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
