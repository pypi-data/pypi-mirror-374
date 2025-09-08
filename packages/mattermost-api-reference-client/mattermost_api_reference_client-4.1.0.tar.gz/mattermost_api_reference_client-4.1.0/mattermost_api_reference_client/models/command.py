from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Command")


@_attrs_define
class Command:
    """
    Attributes:
        id (Union[Unset, str]): The ID of the slash command
        token (Union[Unset, str]): The token which is used to verify the source of the payload
        create_at (Union[Unset, int]): The time in milliseconds the command was created
        update_at (Union[Unset, int]): The time in milliseconds the command was last updated
        delete_at (Union[Unset, int]): The time in milliseconds the command was deleted, 0 if never deleted
        creator_id (Union[Unset, str]): The user id for the commands creator
        team_id (Union[Unset, str]): The team id for which this command is configured
        trigger (Union[Unset, str]): The string that triggers this command
        method (Union[Unset, str]): Is the trigger done with HTTP Get ('G') or HTTP Post ('P')
        username (Union[Unset, str]): What is the username for the response post
        icon_url (Union[Unset, str]): The url to find the icon for this users avatar
        auto_complete (Union[Unset, bool]): Use auto complete for this command
        auto_complete_desc (Union[Unset, str]): The description for this command shown when selecting the command
        auto_complete_hint (Union[Unset, str]): The hint for this command
        display_name (Union[Unset, str]): Display name for the command
        description (Union[Unset, str]): Description for this command
        url (Union[Unset, str]): The URL that is triggered
    """

    id: Union[Unset, str] = UNSET
    token: Union[Unset, str] = UNSET
    create_at: Union[Unset, int] = UNSET
    update_at: Union[Unset, int] = UNSET
    delete_at: Union[Unset, int] = UNSET
    creator_id: Union[Unset, str] = UNSET
    team_id: Union[Unset, str] = UNSET
    trigger: Union[Unset, str] = UNSET
    method: Union[Unset, str] = UNSET
    username: Union[Unset, str] = UNSET
    icon_url: Union[Unset, str] = UNSET
    auto_complete: Union[Unset, bool] = UNSET
    auto_complete_desc: Union[Unset, str] = UNSET
    auto_complete_hint: Union[Unset, str] = UNSET
    display_name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        token = self.token

        create_at = self.create_at

        update_at = self.update_at

        delete_at = self.delete_at

        creator_id = self.creator_id

        team_id = self.team_id

        trigger = self.trigger

        method = self.method

        username = self.username

        icon_url = self.icon_url

        auto_complete = self.auto_complete

        auto_complete_desc = self.auto_complete_desc

        auto_complete_hint = self.auto_complete_hint

        display_name = self.display_name

        description = self.description

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if token is not UNSET:
            field_dict["token"] = token
        if create_at is not UNSET:
            field_dict["create_at"] = create_at
        if update_at is not UNSET:
            field_dict["update_at"] = update_at
        if delete_at is not UNSET:
            field_dict["delete_at"] = delete_at
        if creator_id is not UNSET:
            field_dict["creator_id"] = creator_id
        if team_id is not UNSET:
            field_dict["team_id"] = team_id
        if trigger is not UNSET:
            field_dict["trigger"] = trigger
        if method is not UNSET:
            field_dict["method"] = method
        if username is not UNSET:
            field_dict["username"] = username
        if icon_url is not UNSET:
            field_dict["icon_url"] = icon_url
        if auto_complete is not UNSET:
            field_dict["auto_complete"] = auto_complete
        if auto_complete_desc is not UNSET:
            field_dict["auto_complete_desc"] = auto_complete_desc
        if auto_complete_hint is not UNSET:
            field_dict["auto_complete_hint"] = auto_complete_hint
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if description is not UNSET:
            field_dict["description"] = description
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        token = d.pop("token", UNSET)

        create_at = d.pop("create_at", UNSET)

        update_at = d.pop("update_at", UNSET)

        delete_at = d.pop("delete_at", UNSET)

        creator_id = d.pop("creator_id", UNSET)

        team_id = d.pop("team_id", UNSET)

        trigger = d.pop("trigger", UNSET)

        method = d.pop("method", UNSET)

        username = d.pop("username", UNSET)

        icon_url = d.pop("icon_url", UNSET)

        auto_complete = d.pop("auto_complete", UNSET)

        auto_complete_desc = d.pop("auto_complete_desc", UNSET)

        auto_complete_hint = d.pop("auto_complete_hint", UNSET)

        display_name = d.pop("display_name", UNSET)

        description = d.pop("description", UNSET)

        url = d.pop("url", UNSET)

        command = cls(
            id=id,
            token=token,
            create_at=create_at,
            update_at=update_at,
            delete_at=delete_at,
            creator_id=creator_id,
            team_id=team_id,
            trigger=trigger,
            method=method,
            username=username,
            icon_url=icon_url,
            auto_complete=auto_complete,
            auto_complete_desc=auto_complete_desc,
            auto_complete_hint=auto_complete_hint,
            display_name=display_name,
            description=description,
            url=url,
        )

        command.additional_properties = d
        return command

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
