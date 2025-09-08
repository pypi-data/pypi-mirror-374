from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MoveChannelBody")


@_attrs_define
class MoveChannelBody:
    """
    Attributes:
        team_id (str):
        force (Union[Unset, bool]): Remove members those are not member of target team before moving the channel.
    """

    team_id: str
    force: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        team_id = self.team_id

        force = self.force

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "team_id": team_id,
            }
        )
        if force is not UNSET:
            field_dict["force"] = force

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        team_id = d.pop("team_id")

        force = d.pop("force", UNSET)

        move_channel_body = cls(
            team_id=team_id,
            force=force,
        )

        move_channel_body.additional_properties = d
        return move_channel_body

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
