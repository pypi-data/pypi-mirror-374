from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ChannelNotifyProps")


@_attrs_define
class ChannelNotifyProps:
    """
    Attributes:
        email (Union[Unset, str]): Set to "true" to enable email notifications, "false" to disable, or "default" to use
            the global user notification setting.
        push (Union[Unset, str]): Set to "all" to receive push notifications for all activity, "mention" for mentions
            and direct messages only, "none" to disable, or "default" to use the global user notification setting.
        desktop (Union[Unset, str]): Set to "all" to receive desktop notifications for all activity, "mention" for
            mentions and direct messages only, "none" to disable, or "default" to use the global user notification setting.
        mark_unread (Union[Unset, str]): Set to "all" to mark the channel unread for any new message, "mention" to mark
            unread for new mentions only. Defaults to "all".
    """

    email: Union[Unset, str] = UNSET
    push: Union[Unset, str] = UNSET
    desktop: Union[Unset, str] = UNSET
    mark_unread: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        push = self.push

        desktop = self.desktop

        mark_unread = self.mark_unread

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if email is not UNSET:
            field_dict["email"] = email
        if push is not UNSET:
            field_dict["push"] = push
        if desktop is not UNSET:
            field_dict["desktop"] = desktop
        if mark_unread is not UNSET:
            field_dict["mark_unread"] = mark_unread

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email", UNSET)

        push = d.pop("push", UNSET)

        desktop = d.pop("desktop", UNSET)

        mark_unread = d.pop("mark_unread", UNSET)

        channel_notify_props = cls(
            email=email,
            push=push,
            desktop=desktop,
            mark_unread=mark_unread,
        )

        channel_notify_props.additional_properties = d
        return channel_notify_props

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
