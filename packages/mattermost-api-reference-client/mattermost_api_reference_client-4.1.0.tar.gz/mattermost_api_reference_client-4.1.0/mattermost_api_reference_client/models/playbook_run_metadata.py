from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PlaybookRunMetadata")


@_attrs_define
class PlaybookRunMetadata:
    """
    Attributes:
        channel_name (Union[Unset, str]): Name of the channel associated to the playbook run. Example: server-down-in-
            eu-cluster.
        channel_display_name (Union[Unset, str]): Display name of the channel associated to the playbook run. Example:
            Server down in EU cluster.
        team_name (Union[Unset, str]): Name of the team the playbook run is in. Example: sre-staff.
        num_members (Union[Unset, int]): Number of users that have been members of the playbook run at any point.
            Example: 25.
        total_posts (Union[Unset, int]): Number of posts in the channel associated to the playbook run. Example: 202.
    """

    channel_name: Union[Unset, str] = UNSET
    channel_display_name: Union[Unset, str] = UNSET
    team_name: Union[Unset, str] = UNSET
    num_members: Union[Unset, int] = UNSET
    total_posts: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        channel_name = self.channel_name

        channel_display_name = self.channel_display_name

        team_name = self.team_name

        num_members = self.num_members

        total_posts = self.total_posts

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if channel_name is not UNSET:
            field_dict["channel_name"] = channel_name
        if channel_display_name is not UNSET:
            field_dict["channel_display_name"] = channel_display_name
        if team_name is not UNSET:
            field_dict["team_name"] = team_name
        if num_members is not UNSET:
            field_dict["num_members"] = num_members
        if total_posts is not UNSET:
            field_dict["total_posts"] = total_posts

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        channel_name = d.pop("channel_name", UNSET)

        channel_display_name = d.pop("channel_display_name", UNSET)

        team_name = d.pop("team_name", UNSET)

        num_members = d.pop("num_members", UNSET)

        total_posts = d.pop("total_posts", UNSET)

        playbook_run_metadata = cls(
            channel_name=channel_name,
            channel_display_name=channel_display_name,
            team_name=team_name,
            num_members=num_members,
            total_posts=total_posts,
        )

        playbook_run_metadata.additional_properties = d
        return playbook_run_metadata

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
