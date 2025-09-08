from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Bot")


@_attrs_define
class Bot:
    """A bot account

    Attributes:
        user_id (Union[Unset, str]): The user id of the associated user entry.
        create_at (Union[Unset, int]): The time in milliseconds a bot was created
        update_at (Union[Unset, int]): The time in milliseconds a bot was last updated
        delete_at (Union[Unset, int]): The time in milliseconds a bot was deleted
        username (Union[Unset, str]):
        display_name (Union[Unset, str]):
        description (Union[Unset, str]):
        owner_id (Union[Unset, str]): The user id of the user that currently owns this bot.
    """

    user_id: Union[Unset, str] = UNSET
    create_at: Union[Unset, int] = UNSET
    update_at: Union[Unset, int] = UNSET
    delete_at: Union[Unset, int] = UNSET
    username: Union[Unset, str] = UNSET
    display_name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    owner_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_id = self.user_id

        create_at = self.create_at

        update_at = self.update_at

        delete_at = self.delete_at

        username = self.username

        display_name = self.display_name

        description = self.description

        owner_id = self.owner_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if create_at is not UNSET:
            field_dict["create_at"] = create_at
        if update_at is not UNSET:
            field_dict["update_at"] = update_at
        if delete_at is not UNSET:
            field_dict["delete_at"] = delete_at
        if username is not UNSET:
            field_dict["username"] = username
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if description is not UNSET:
            field_dict["description"] = description
        if owner_id is not UNSET:
            field_dict["owner_id"] = owner_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        user_id = d.pop("user_id", UNSET)

        create_at = d.pop("create_at", UNSET)

        update_at = d.pop("update_at", UNSET)

        delete_at = d.pop("delete_at", UNSET)

        username = d.pop("username", UNSET)

        display_name = d.pop("display_name", UNSET)

        description = d.pop("description", UNSET)

        owner_id = d.pop("owner_id", UNSET)

        bot = cls(
            user_id=user_id,
            create_at=create_at,
            update_at=update_at,
            delete_at=delete_at,
            username=username,
            display_name=display_name,
            description=description,
            owner_id=owner_id,
        )

        bot.additional_properties = d
        return bot

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
