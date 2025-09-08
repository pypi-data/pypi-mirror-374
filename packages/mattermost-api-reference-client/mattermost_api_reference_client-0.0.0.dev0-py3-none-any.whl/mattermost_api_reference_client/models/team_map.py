from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.team import Team


T = TypeVar("T", bound="TeamMap")


@_attrs_define
class TeamMap:
    """A mapping of teamIds to teams.

    Attributes:
        team_id (Union[Unset, Team]):
    """

    team_id: Union[Unset, "Team"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        team_id: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.team_id, Unset):
            team_id = self.team_id.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if team_id is not UNSET:
            field_dict["team_id"] = team_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.team import Team

        d = dict(src_dict)
        _team_id = d.pop("team_id", UNSET)
        team_id: Union[Unset, Team]
        if isinstance(_team_id, Unset):
            team_id = UNSET
        else:
            team_id = Team.from_dict(_team_id)

        team_map = cls(
            team_id=team_id,
        )

        team_map.additional_properties = d
        return team_map

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
