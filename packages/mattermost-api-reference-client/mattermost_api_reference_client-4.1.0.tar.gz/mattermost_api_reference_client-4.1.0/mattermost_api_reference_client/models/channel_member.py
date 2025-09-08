from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.channel_notify_props import ChannelNotifyProps


T = TypeVar("T", bound="ChannelMember")


@_attrs_define
class ChannelMember:
    """
    Attributes:
        channel_id (Union[Unset, str]):
        user_id (Union[Unset, str]):
        roles (Union[Unset, str]):
        last_viewed_at (Union[Unset, int]): The time in milliseconds the channel was last viewed by the user
        msg_count (Union[Unset, int]):
        mention_count (Union[Unset, int]):
        notify_props (Union[Unset, ChannelNotifyProps]):
        last_update_at (Union[Unset, int]): The time in milliseconds the channel member was last updated
    """

    channel_id: Union[Unset, str] = UNSET
    user_id: Union[Unset, str] = UNSET
    roles: Union[Unset, str] = UNSET
    last_viewed_at: Union[Unset, int] = UNSET
    msg_count: Union[Unset, int] = UNSET
    mention_count: Union[Unset, int] = UNSET
    notify_props: Union[Unset, "ChannelNotifyProps"] = UNSET
    last_update_at: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        channel_id = self.channel_id

        user_id = self.user_id

        roles = self.roles

        last_viewed_at = self.last_viewed_at

        msg_count = self.msg_count

        mention_count = self.mention_count

        notify_props: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.notify_props, Unset):
            notify_props = self.notify_props.to_dict()

        last_update_at = self.last_update_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if channel_id is not UNSET:
            field_dict["channel_id"] = channel_id
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if roles is not UNSET:
            field_dict["roles"] = roles
        if last_viewed_at is not UNSET:
            field_dict["last_viewed_at"] = last_viewed_at
        if msg_count is not UNSET:
            field_dict["msg_count"] = msg_count
        if mention_count is not UNSET:
            field_dict["mention_count"] = mention_count
        if notify_props is not UNSET:
            field_dict["notify_props"] = notify_props
        if last_update_at is not UNSET:
            field_dict["last_update_at"] = last_update_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.channel_notify_props import ChannelNotifyProps

        d = dict(src_dict)
        channel_id = d.pop("channel_id", UNSET)

        user_id = d.pop("user_id", UNSET)

        roles = d.pop("roles", UNSET)

        last_viewed_at = d.pop("last_viewed_at", UNSET)

        msg_count = d.pop("msg_count", UNSET)

        mention_count = d.pop("mention_count", UNSET)

        _notify_props = d.pop("notify_props", UNSET)
        notify_props: Union[Unset, ChannelNotifyProps]
        if isinstance(_notify_props, Unset):
            notify_props = UNSET
        else:
            notify_props = ChannelNotifyProps.from_dict(_notify_props)

        last_update_at = d.pop("last_update_at", UNSET)

        channel_member = cls(
            channel_id=channel_id,
            user_id=user_id,
            roles=roles,
            last_viewed_at=last_viewed_at,
            msg_count=msg_count,
            mention_count=mention_count,
            notify_props=notify_props,
            last_update_at=last_update_at,
        )

        channel_member.additional_properties = d
        return channel_member

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
