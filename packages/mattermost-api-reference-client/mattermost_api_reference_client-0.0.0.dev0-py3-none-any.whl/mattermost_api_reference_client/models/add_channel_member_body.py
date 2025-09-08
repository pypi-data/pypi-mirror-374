from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AddChannelMemberBody")


@_attrs_define
class AddChannelMemberBody:
    """
    Attributes:
        user_id (Union[Unset, str]): The ID of user to add into the channel, for backwards compatibility.
        user_ids (Union[Unset, list[str]]): The IDs of users to add into the channel, required if 'user_id' doess not
            exist.
        post_root_id (Union[Unset, str]): The ID of root post where link to add channel member originates
    """

    user_id: Union[Unset, str] = UNSET
    user_ids: Union[Unset, list[str]] = UNSET
    post_root_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_id = self.user_id

        user_ids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.user_ids, Unset):
            user_ids = self.user_ids

        post_root_id = self.post_root_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if user_ids is not UNSET:
            field_dict["user_ids"] = user_ids
        if post_root_id is not UNSET:
            field_dict["post_root_id"] = post_root_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        user_id = d.pop("user_id", UNSET)

        user_ids = cast(list[str], d.pop("user_ids", UNSET))

        post_root_id = d.pop("post_root_id", UNSET)

        add_channel_member_body = cls(
            user_id=user_id,
            user_ids=user_ids,
            post_root_id=post_root_id,
        )

        add_channel_member_body.additional_properties = d
        return add_channel_member_body

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
