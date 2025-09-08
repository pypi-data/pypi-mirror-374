from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateIncomingWebhookBody")


@_attrs_define
class UpdateIncomingWebhookBody:
    """
    Attributes:
        id (str): Incoming webhook GUID
        channel_id (str): The ID of a public channel or private group that receives the webhook payloads.
        display_name (str): The display name for this incoming webhook
        description (str): The description for this incoming webhook
        username (Union[Unset, str]): The username this incoming webhook will post as.
        icon_url (Union[Unset, str]): The profile picture this incoming webhook will use when posting.
    """

    id: str
    channel_id: str
    display_name: str
    description: str
    username: Union[Unset, str] = UNSET
    icon_url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        channel_id = self.channel_id

        display_name = self.display_name

        description = self.description

        username = self.username

        icon_url = self.icon_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "channel_id": channel_id,
                "display_name": display_name,
                "description": description,
            }
        )
        if username is not UNSET:
            field_dict["username"] = username
        if icon_url is not UNSET:
            field_dict["icon_url"] = icon_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        channel_id = d.pop("channel_id")

        display_name = d.pop("display_name")

        description = d.pop("description")

        username = d.pop("username", UNSET)

        icon_url = d.pop("icon_url", UNSET)

        update_incoming_webhook_body = cls(
            id=id,
            channel_id=channel_id,
            display_name=display_name,
            description=description,
            username=username,
            icon_url=icon_url,
        )

        update_incoming_webhook_body.additional_properties = d
        return update_incoming_webhook_body

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
