from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DataRetentionPolicyWithTeamAndChannelCounts")


@_attrs_define
class DataRetentionPolicyWithTeamAndChannelCounts:
    """
    Attributes:
        display_name (Union[Unset, str]): The display name for this retention policy.
        post_duration (Union[Unset, int]): The number of days a message will be retained before being deleted by this
            policy. If this value is less than 0, the policy has infinite retention (i.e. messages are never deleted).
        id (Union[Unset, str]): The ID of this retention policy.
        team_count (Union[Unset, int]): The number of teams to which this policy is applied.
        channel_count (Union[Unset, int]): The number of channels to which this policy is applied.
    """

    display_name: Union[Unset, str] = UNSET
    post_duration: Union[Unset, int] = UNSET
    id: Union[Unset, str] = UNSET
    team_count: Union[Unset, int] = UNSET
    channel_count: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        display_name = self.display_name

        post_duration = self.post_duration

        id = self.id

        team_count = self.team_count

        channel_count = self.channel_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if post_duration is not UNSET:
            field_dict["post_duration"] = post_duration
        if id is not UNSET:
            field_dict["id"] = id
        if team_count is not UNSET:
            field_dict["team_count"] = team_count
        if channel_count is not UNSET:
            field_dict["channel_count"] = channel_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        display_name = d.pop("display_name", UNSET)

        post_duration = d.pop("post_duration", UNSET)

        id = d.pop("id", UNSET)

        team_count = d.pop("team_count", UNSET)

        channel_count = d.pop("channel_count", UNSET)

        data_retention_policy_with_team_and_channel_counts = cls(
            display_name=display_name,
            post_duration=post_duration,
            id=id,
            team_count=team_count,
            channel_count=channel_count,
        )

        data_retention_policy_with_team_and_channel_counts.additional_properties = d
        return data_retention_policy_with_team_and_channel_counts

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
