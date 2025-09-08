from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateIncomingWebhookBody")


@_attrs_define
class CreateIncomingWebhookBody:
    """
    Attributes:
        channel_id (str): The ID of a public channel or private group that receives the webhook payloads.
        user_id (Union[Unset, str]): The ID of the owner of the webhook if different than the requester. Required for
            [local mode](https://docs.mattermost.com/administration/mmctl-cli-tool.html#local-mode).
        display_name (Union[Unset, str]): The display name for this incoming webhook
        description (Union[Unset, str]): The description for this incoming webhook
        username (Union[Unset, str]): The username this incoming webhook will post as.
        icon_url (Union[Unset, str]): The profile picture this incoming webhook will use when posting.
    """

    channel_id: str
    user_id: Union[Unset, str] = UNSET
    display_name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    username: Union[Unset, str] = UNSET
    icon_url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        channel_id = self.channel_id

        user_id = self.user_id

        display_name = self.display_name

        description = self.description

        username = self.username

        icon_url = self.icon_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "channel_id": channel_id,
            }
        )
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if description is not UNSET:
            field_dict["description"] = description
        if username is not UNSET:
            field_dict["username"] = username
        if icon_url is not UNSET:
            field_dict["icon_url"] = icon_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        channel_id = d.pop("channel_id")

        user_id = d.pop("user_id", UNSET)

        display_name = d.pop("display_name", UNSET)

        description = d.pop("description", UNSET)

        username = d.pop("username", UNSET)

        icon_url = d.pop("icon_url", UNSET)

        create_incoming_webhook_body = cls(
            channel_id=channel_id,
            user_id=user_id,
            display_name=display_name,
            description=description,
            username=username,
            icon_url=icon_url,
        )

        create_incoming_webhook_body.additional_properties = d
        return create_incoming_webhook_body

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
