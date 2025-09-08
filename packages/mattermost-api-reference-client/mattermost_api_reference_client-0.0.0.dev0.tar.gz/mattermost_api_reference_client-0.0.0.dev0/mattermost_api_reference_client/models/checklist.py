from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.checklist_item import ChecklistItem


T = TypeVar("T", bound="Checklist")


@_attrs_define
class Checklist:
    """
    Attributes:
        id (Union[Unset, str]): A unique, 26 characters long, alphanumeric identifier for the checklist. Example:
            6f6nsgxzoq84fqh1dnlyivgafd.
        title (Union[Unset, str]): The title of the checklist. Example: Triage issue.
        items (Union[Unset, list['ChecklistItem']]): The list of tasks to do.
    """

    id: Union[Unset, str] = UNSET
    title: Union[Unset, str] = UNSET
    items: Union[Unset, list["ChecklistItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        title = self.title

        items: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.items, Unset):
            items = []
            for items_item_data in self.items:
                items_item = items_item_data.to_dict()
                items.append(items_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if title is not UNSET:
            field_dict["title"] = title
        if items is not UNSET:
            field_dict["items"] = items

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.checklist_item import ChecklistItem

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        title = d.pop("title", UNSET)

        items = []
        _items = d.pop("items", UNSET)
        for items_item_data in _items or []:
            items_item = ChecklistItem.from_dict(items_item_data)

            items.append(items_item)

        checklist = cls(
            id=id,
            title=title,
            items=items,
        )

        checklist.additional_properties = d
        return checklist

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
