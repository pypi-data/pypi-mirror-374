from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="TeamUnread")


@_attrs_define
class TeamUnread:
    """
    Attributes:
        team_id (Union[Unset, str]):
        msg_count (Union[Unset, int]):
        mention_count (Union[Unset, int]):
    """

    team_id: Union[Unset, str] = UNSET
    msg_count: Union[Unset, int] = UNSET
    mention_count: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        team_id = self.team_id

        msg_count = self.msg_count

        mention_count = self.mention_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if team_id is not UNSET:
            field_dict["team_id"] = team_id
        if msg_count is not UNSET:
            field_dict["msg_count"] = msg_count
        if mention_count is not UNSET:
            field_dict["mention_count"] = mention_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        team_id = d.pop("team_id", UNSET)

        msg_count = d.pop("msg_count", UNSET)

        mention_count = d.pop("mention_count", UNSET)

        team_unread = cls(
            team_id=team_id,
            msg_count=msg_count,
            mention_count=mention_count,
        )

        team_unread.additional_properties = d
        return team_unread

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
