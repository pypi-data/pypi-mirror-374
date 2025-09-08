from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AcceptRemoteClusterInviteBody")


@_attrs_define
class AcceptRemoteClusterInviteBody:
    """
    Attributes:
        invite (str):
        name (str):
        default_team_id (str):
        password (str): The password to decrypt the invite code.
        display_name (Union[Unset, str]):
    """

    invite: str
    name: str
    default_team_id: str
    password: str
    display_name: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        invite = self.invite

        name = self.name

        default_team_id = self.default_team_id

        password = self.password

        display_name = self.display_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "invite": invite,
                "name": name,
                "default_team_id": default_team_id,
                "password": password,
            }
        )
        if display_name is not UNSET:
            field_dict["display_name"] = display_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        invite = d.pop("invite")

        name = d.pop("name")

        default_team_id = d.pop("default_team_id")

        password = d.pop("password")

        display_name = d.pop("display_name", UNSET)

        accept_remote_cluster_invite_body = cls(
            invite=invite,
            name=name,
            default_team_id=default_team_id,
            password=password,
            display_name=display_name,
        )

        accept_remote_cluster_invite_body.additional_properties = d
        return accept_remote_cluster_invite_body

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
