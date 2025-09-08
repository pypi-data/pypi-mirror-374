from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user import User


T = TypeVar("T", bound="GetGroupUsersResponse200")


@_attrs_define
class GetGroupUsersResponse200:
    """
    Attributes:
        members (Union[Unset, list['User']]):
        total_member_count (Union[Unset, int]):
    """

    members: Union[Unset, list["User"]] = UNSET
    total_member_count: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        members: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.members, Unset):
            members = []
            for members_item_data in self.members:
                members_item = members_item_data.to_dict()
                members.append(members_item)

        total_member_count = self.total_member_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if members is not UNSET:
            field_dict["members"] = members
        if total_member_count is not UNSET:
            field_dict["total_member_count"] = total_member_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user import User

        d = dict(src_dict)
        members = []
        _members = d.pop("members", UNSET)
        for members_item_data in _members or []:
            members_item = User.from_dict(members_item_data)

            members.append(members_item)

        total_member_count = d.pop("total_member_count", UNSET)

        get_group_users_response_200 = cls(
            members=members,
            total_member_count=total_member_count,
        )

        get_group_users_response_200.additional_properties = d
        return get_group_users_response_200

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
