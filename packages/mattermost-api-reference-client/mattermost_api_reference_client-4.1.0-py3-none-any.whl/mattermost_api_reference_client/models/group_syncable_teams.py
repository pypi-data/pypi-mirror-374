from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GroupSyncableTeams")


@_attrs_define
class GroupSyncableTeams:
    """
    Attributes:
        team_id (Union[Unset, str]):
        team_display_name (Union[Unset, str]):
        team_type (Union[Unset, str]):
        group_id (Union[Unset, str]):
        auto_add (Union[Unset, bool]):
        create_at (Union[Unset, int]):
        delete_at (Union[Unset, int]):
        update_at (Union[Unset, int]):
    """

    team_id: Union[Unset, str] = UNSET
    team_display_name: Union[Unset, str] = UNSET
    team_type: Union[Unset, str] = UNSET
    group_id: Union[Unset, str] = UNSET
    auto_add: Union[Unset, bool] = UNSET
    create_at: Union[Unset, int] = UNSET
    delete_at: Union[Unset, int] = UNSET
    update_at: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        team_id = self.team_id

        team_display_name = self.team_display_name

        team_type = self.team_type

        group_id = self.group_id

        auto_add = self.auto_add

        create_at = self.create_at

        delete_at = self.delete_at

        update_at = self.update_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if team_id is not UNSET:
            field_dict["team_id"] = team_id
        if team_display_name is not UNSET:
            field_dict["team_display_name"] = team_display_name
        if team_type is not UNSET:
            field_dict["team_type"] = team_type
        if group_id is not UNSET:
            field_dict["group_id"] = group_id
        if auto_add is not UNSET:
            field_dict["auto_add"] = auto_add
        if create_at is not UNSET:
            field_dict["create_at"] = create_at
        if delete_at is not UNSET:
            field_dict["delete_at"] = delete_at
        if update_at is not UNSET:
            field_dict["update_at"] = update_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        team_id = d.pop("team_id", UNSET)

        team_display_name = d.pop("team_display_name", UNSET)

        team_type = d.pop("team_type", UNSET)

        group_id = d.pop("group_id", UNSET)

        auto_add = d.pop("auto_add", UNSET)

        create_at = d.pop("create_at", UNSET)

        delete_at = d.pop("delete_at", UNSET)

        update_at = d.pop("update_at", UNSET)

        group_syncable_teams = cls(
            team_id=team_id,
            team_display_name=team_display_name,
            team_type=team_type,
            group_id=group_id,
            auto_add=auto_add,
            create_at=create_at,
            delete_at=delete_at,
            update_at=update_at,
        )

        group_syncable_teams.additional_properties = d
        return group_syncable_teams

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
