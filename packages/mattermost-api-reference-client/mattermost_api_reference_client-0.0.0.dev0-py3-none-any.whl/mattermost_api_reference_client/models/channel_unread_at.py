from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ChannelUnreadAt")


@_attrs_define
class ChannelUnreadAt:
    """
    Attributes:
        team_id (Union[Unset, str]): The ID of the team the channel belongs to.
        channel_id (Union[Unset, str]): The ID of the channel the user has access to..
        msg_count (Union[Unset, int]): No. of messages the user has already read.
        mention_count (Union[Unset, int]): No. of mentions the user has within the unread posts of the channel.
        last_viewed_at (Union[Unset, int]): time in milliseconds when the user last viewed the channel.
    """

    team_id: Union[Unset, str] = UNSET
    channel_id: Union[Unset, str] = UNSET
    msg_count: Union[Unset, int] = UNSET
    mention_count: Union[Unset, int] = UNSET
    last_viewed_at: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        team_id = self.team_id

        channel_id = self.channel_id

        msg_count = self.msg_count

        mention_count = self.mention_count

        last_viewed_at = self.last_viewed_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if team_id is not UNSET:
            field_dict["team_id"] = team_id
        if channel_id is not UNSET:
            field_dict["channel_id"] = channel_id
        if msg_count is not UNSET:
            field_dict["msg_count"] = msg_count
        if mention_count is not UNSET:
            field_dict["mention_count"] = mention_count
        if last_viewed_at is not UNSET:
            field_dict["last_viewed_at"] = last_viewed_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        team_id = d.pop("team_id", UNSET)

        channel_id = d.pop("channel_id", UNSET)

        msg_count = d.pop("msg_count", UNSET)

        mention_count = d.pop("mention_count", UNSET)

        last_viewed_at = d.pop("last_viewed_at", UNSET)

        channel_unread_at = cls(
            team_id=team_id,
            channel_id=channel_id,
            msg_count=msg_count,
            mention_count=mention_count,
            last_viewed_at=last_viewed_at,
        )

        channel_unread_at.additional_properties = d
        return channel_unread_at

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
