from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateOutgoingWebhookBody")


@_attrs_define
class CreateOutgoingWebhookBody:
    """
    Attributes:
        team_id (str): The ID of the team that the webhook watchs
        display_name (str): The display name for this outgoing webhook
        trigger_words (list[str]): List of words for the webhook to trigger on
        callback_urls (list[str]): The URLs to POST the payloads to when the webhook is triggered
        channel_id (Union[Unset, str]): The ID of a public channel that the webhook watchs
        creator_id (Union[Unset, str]): The ID of the owner of the webhook if different than the requester. Required in
            [local mode](https://docs.mattermost.com/administration/mmctl-cli-tool.html#local-mode).
        description (Union[Unset, str]): The description for this outgoing webhook
        trigger_when (Union[Unset, int]): When to trigger the webhook, `0` when a trigger word is present at all and `1`
            if the message starts with a trigger word
        content_type (Union[Unset, str]): The format to POST the data in, either `application/json` or
            `application/x-www-form-urlencoded` Default: 'application/x-www-form-urlencoded'.
    """

    team_id: str
    display_name: str
    trigger_words: list[str]
    callback_urls: list[str]
    channel_id: Union[Unset, str] = UNSET
    creator_id: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    trigger_when: Union[Unset, int] = UNSET
    content_type: Union[Unset, str] = "application/x-www-form-urlencoded"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        team_id = self.team_id

        display_name = self.display_name

        trigger_words = self.trigger_words

        callback_urls = self.callback_urls

        channel_id = self.channel_id

        creator_id = self.creator_id

        description = self.description

        trigger_when = self.trigger_when

        content_type = self.content_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "team_id": team_id,
                "display_name": display_name,
                "trigger_words": trigger_words,
                "callback_urls": callback_urls,
            }
        )
        if channel_id is not UNSET:
            field_dict["channel_id"] = channel_id
        if creator_id is not UNSET:
            field_dict["creator_id"] = creator_id
        if description is not UNSET:
            field_dict["description"] = description
        if trigger_when is not UNSET:
            field_dict["trigger_when"] = trigger_when
        if content_type is not UNSET:
            field_dict["content_type"] = content_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        team_id = d.pop("team_id")

        display_name = d.pop("display_name")

        trigger_words = cast(list[str], d.pop("trigger_words"))

        callback_urls = cast(list[str], d.pop("callback_urls"))

        channel_id = d.pop("channel_id", UNSET)

        creator_id = d.pop("creator_id", UNSET)

        description = d.pop("description", UNSET)

        trigger_when = d.pop("trigger_when", UNSET)

        content_type = d.pop("content_type", UNSET)

        create_outgoing_webhook_body = cls(
            team_id=team_id,
            display_name=display_name,
            trigger_words=trigger_words,
            callback_urls=callback_urls,
            channel_id=channel_id,
            creator_id=creator_id,
            description=description,
            trigger_when=trigger_when,
            content_type=content_type,
        )

        create_outgoing_webhook_body.additional_properties = d
        return create_outgoing_webhook_body

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
