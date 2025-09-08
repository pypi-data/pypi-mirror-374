from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DataRetentionPolicyForTeam")


@_attrs_define
class DataRetentionPolicyForTeam:
    """
    Attributes:
        team_id (Union[Unset, str]): The team ID.
        post_duration (Union[Unset, int]): The number of days a message will be retained before being deleted by this
            policy.
    """

    team_id: Union[Unset, str] = UNSET
    post_duration: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        team_id = self.team_id

        post_duration = self.post_duration

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if team_id is not UNSET:
            field_dict["team_id"] = team_id
        if post_duration is not UNSET:
            field_dict["post_duration"] = post_duration

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        team_id = d.pop("team_id", UNSET)

        post_duration = d.pop("post_duration", UNSET)

        data_retention_policy_for_team = cls(
            team_id=team_id,
            post_duration=post_duration,
        )

        data_retention_policy_for_team.additional_properties = d
        return data_retention_policy_for_team

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
