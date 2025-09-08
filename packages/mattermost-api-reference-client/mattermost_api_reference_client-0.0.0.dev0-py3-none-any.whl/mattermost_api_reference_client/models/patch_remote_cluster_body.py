from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PatchRemoteClusterBody")


@_attrs_define
class PatchRemoteClusterBody:
    """
    Attributes:
        display_name (Union[Unset, str]):
        default_team_id (Union[Unset, str]): The team where channels from invites are created
    """

    display_name: Union[Unset, str] = UNSET
    default_team_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        display_name = self.display_name

        default_team_id = self.default_team_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if default_team_id is not UNSET:
            field_dict["default_team_id"] = default_team_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        display_name = d.pop("display_name", UNSET)

        default_team_id = d.pop("default_team_id", UNSET)

        patch_remote_cluster_body = cls(
            display_name=display_name,
            default_team_id=default_team_id,
        )

        patch_remote_cluster_body.additional_properties = d
        return patch_remote_cluster_body

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
