from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.new_team_member import NewTeamMember


T = TypeVar("T", bound="NewTeamMembersList")


@_attrs_define
class NewTeamMembersList:
    """
    Attributes:
        has_next (Union[Unset, bool]): Indicates if there is another page of new team members that can be fetched.
        items (Union[Unset, list['NewTeamMember']]): List of new team members.
        total_count (Union[Unset, int]): The total count of new team members for the given time range.
    """

    has_next: Union[Unset, bool] = UNSET
    items: Union[Unset, list["NewTeamMember"]] = UNSET
    total_count: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        has_next = self.has_next

        items: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.items, Unset):
            items = []
            for items_item_data in self.items:
                items_item = items_item_data.to_dict()
                items.append(items_item)

        total_count = self.total_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if has_next is not UNSET:
            field_dict["has_next"] = has_next
        if items is not UNSET:
            field_dict["items"] = items
        if total_count is not UNSET:
            field_dict["total_count"] = total_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.new_team_member import NewTeamMember

        d = dict(src_dict)
        has_next = d.pop("has_next", UNSET)

        items = []
        _items = d.pop("items", UNSET)
        for items_item_data in _items or []:
            items_item = NewTeamMember.from_dict(items_item_data)

            items.append(items_item)

        total_count = d.pop("total_count", UNSET)

        new_team_members_list = cls(
            has_next=has_next,
            items=items,
            total_count=total_count,
        )

        new_team_members_list.additional_properties = d
        return new_team_members_list

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
