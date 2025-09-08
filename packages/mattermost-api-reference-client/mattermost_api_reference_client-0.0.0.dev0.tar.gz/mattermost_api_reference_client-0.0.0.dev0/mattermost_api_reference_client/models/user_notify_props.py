from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UserNotifyProps")


@_attrs_define
class UserNotifyProps:
    """
    Attributes:
        email (Union[Unset, str]): Set to "true" to enable email notifications, "false" to disable. Defaults to "true".
        push (Union[Unset, str]): Set to "all" to receive push notifications for all activity, "mention" for mentions
            and direct messages only, and "none" to disable. Defaults to "mention".
        desktop (Union[Unset, str]): Set to "all" to receive desktop notifications for all activity, "mention" for
            mentions and direct messages only, and "none" to disable. Defaults to "all".
        desktop_sound (Union[Unset, str]): Set to "true" to enable sound on desktop notifications, "false" to disable.
            Defaults to "true".
        mention_keys (Union[Unset, str]): A comma-separated list of words to count as mentions. Defaults to username and
            @username.
        channel (Union[Unset, str]): Set to "true" to enable channel-wide notifications (@channel, @all, etc.), "false"
            to disable. Defaults to "true".
        first_name (Union[Unset, str]): Set to "true" to enable mentions for first name. Defaults to "true" if a first
            name is set, "false" otherwise.
    """

    email: Union[Unset, str] = UNSET
    push: Union[Unset, str] = UNSET
    desktop: Union[Unset, str] = UNSET
    desktop_sound: Union[Unset, str] = UNSET
    mention_keys: Union[Unset, str] = UNSET
    channel: Union[Unset, str] = UNSET
    first_name: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        push = self.push

        desktop = self.desktop

        desktop_sound = self.desktop_sound

        mention_keys = self.mention_keys

        channel = self.channel

        first_name = self.first_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if email is not UNSET:
            field_dict["email"] = email
        if push is not UNSET:
            field_dict["push"] = push
        if desktop is not UNSET:
            field_dict["desktop"] = desktop
        if desktop_sound is not UNSET:
            field_dict["desktop_sound"] = desktop_sound
        if mention_keys is not UNSET:
            field_dict["mention_keys"] = mention_keys
        if channel is not UNSET:
            field_dict["channel"] = channel
        if first_name is not UNSET:
            field_dict["first_name"] = first_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email", UNSET)

        push = d.pop("push", UNSET)

        desktop = d.pop("desktop", UNSET)

        desktop_sound = d.pop("desktop_sound", UNSET)

        mention_keys = d.pop("mention_keys", UNSET)

        channel = d.pop("channel", UNSET)

        first_name = d.pop("first_name", UNSET)

        user_notify_props = cls(
            email=email,
            push=push,
            desktop=desktop,
            desktop_sound=desktop_sound,
            mention_keys=mention_keys,
            channel=channel,
            first_name=first_name,
        )

        user_notify_props.additional_properties = d
        return user_notify_props

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
