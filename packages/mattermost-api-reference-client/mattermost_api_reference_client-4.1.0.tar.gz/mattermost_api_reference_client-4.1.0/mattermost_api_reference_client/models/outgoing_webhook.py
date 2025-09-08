from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OutgoingWebhook")


@_attrs_define
class OutgoingWebhook:
    """
    Attributes:
        id (Union[Unset, str]): The unique identifier for this outgoing webhook
        create_at (Union[Unset, int]): The time in milliseconds a outgoing webhook was created
        update_at (Union[Unset, int]): The time in milliseconds a outgoing webhook was last updated
        delete_at (Union[Unset, int]): The time in milliseconds a outgoing webhook was deleted
        creator_id (Union[Unset, str]): The Id of the user who created the webhook
        team_id (Union[Unset, str]): The ID of the team that the webhook watchs
        channel_id (Union[Unset, str]): The ID of a public channel that the webhook watchs
        description (Union[Unset, str]): The description for this outgoing webhook
        display_name (Union[Unset, str]): The display name for this outgoing webhook
        trigger_words (Union[Unset, list[str]]): List of words for the webhook to trigger on
        trigger_when (Union[Unset, int]): When to trigger the webhook, `0` when a trigger word is present at all and `1`
            if the message starts with a trigger word
        callback_urls (Union[Unset, list[str]]): The URLs to POST the payloads to when the webhook is triggered
        content_type (Union[Unset, str]): The format to POST the data in, either `application/json` or
            `application/x-www-form-urlencoded` Default: 'application/x-www-form-urlencoded'.
    """

    id: Union[Unset, str] = UNSET
    create_at: Union[Unset, int] = UNSET
    update_at: Union[Unset, int] = UNSET
    delete_at: Union[Unset, int] = UNSET
    creator_id: Union[Unset, str] = UNSET
    team_id: Union[Unset, str] = UNSET
    channel_id: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    display_name: Union[Unset, str] = UNSET
    trigger_words: Union[Unset, list[str]] = UNSET
    trigger_when: Union[Unset, int] = UNSET
    callback_urls: Union[Unset, list[str]] = UNSET
    content_type: Union[Unset, str] = "application/x-www-form-urlencoded"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        create_at = self.create_at

        update_at = self.update_at

        delete_at = self.delete_at

        creator_id = self.creator_id

        team_id = self.team_id

        channel_id = self.channel_id

        description = self.description

        display_name = self.display_name

        trigger_words: Union[Unset, list[str]] = UNSET
        if not isinstance(self.trigger_words, Unset):
            trigger_words = self.trigger_words

        trigger_when = self.trigger_when

        callback_urls: Union[Unset, list[str]] = UNSET
        if not isinstance(self.callback_urls, Unset):
            callback_urls = self.callback_urls

        content_type = self.content_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
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
        if channel_id is not UNSET:
            field_dict["channel_id"] = channel_id
        if description is not UNSET:
            field_dict["description"] = description
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if trigger_words is not UNSET:
            field_dict["trigger_words"] = trigger_words
        if trigger_when is not UNSET:
            field_dict["trigger_when"] = trigger_when
        if callback_urls is not UNSET:
            field_dict["callback_urls"] = callback_urls
        if content_type is not UNSET:
            field_dict["content_type"] = content_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        create_at = d.pop("create_at", UNSET)

        update_at = d.pop("update_at", UNSET)

        delete_at = d.pop("delete_at", UNSET)

        creator_id = d.pop("creator_id", UNSET)

        team_id = d.pop("team_id", UNSET)

        channel_id = d.pop("channel_id", UNSET)

        description = d.pop("description", UNSET)

        display_name = d.pop("display_name", UNSET)

        trigger_words = cast(list[str], d.pop("trigger_words", UNSET))

        trigger_when = d.pop("trigger_when", UNSET)

        callback_urls = cast(list[str], d.pop("callback_urls", UNSET))

        content_type = d.pop("content_type", UNSET)

        outgoing_webhook = cls(
            id=id,
            create_at=create_at,
            update_at=update_at,
            delete_at=delete_at,
            creator_id=creator_id,
            team_id=team_id,
            channel_id=channel_id,
            description=description,
            display_name=display_name,
            trigger_words=trigger_words,
            trigger_when=trigger_when,
            callback_urls=callback_urls,
            content_type=content_type,
        )

        outgoing_webhook.additional_properties = d
        return outgoing_webhook

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
