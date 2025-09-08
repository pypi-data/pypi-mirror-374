from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user import User


T = TypeVar("T", bound="UserAutocomplete")


@_attrs_define
class UserAutocomplete:
    """
    Attributes:
        users (Union[Unset, list['User']]): A list of users that are the main result of the query
        out_of_channel (Union[Unset, list['User']]): A special case list of users returned when autocompleting in a
            specific channel. Omitted when empty or not relevant
    """

    users: Union[Unset, list["User"]] = UNSET
    out_of_channel: Union[Unset, list["User"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        users: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.users, Unset):
            users = []
            for users_item_data in self.users:
                users_item = users_item_data.to_dict()
                users.append(users_item)

        out_of_channel: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.out_of_channel, Unset):
            out_of_channel = []
            for out_of_channel_item_data in self.out_of_channel:
                out_of_channel_item = out_of_channel_item_data.to_dict()
                out_of_channel.append(out_of_channel_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if users is not UNSET:
            field_dict["users"] = users
        if out_of_channel is not UNSET:
            field_dict["out_of_channel"] = out_of_channel

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user import User

        d = dict(src_dict)
        users = []
        _users = d.pop("users", UNSET)
        for users_item_data in _users or []:
            users_item = User.from_dict(users_item_data)

            users.append(users_item)

        out_of_channel = []
        _out_of_channel = d.pop("out_of_channel", UNSET)
        for out_of_channel_item_data in _out_of_channel or []:
            out_of_channel_item = User.from_dict(out_of_channel_item_data)

            out_of_channel.append(out_of_channel_item)

        user_autocomplete = cls(
            users=users,
            out_of_channel=out_of_channel,
        )

        user_autocomplete.additional_properties = d
        return user_autocomplete

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
