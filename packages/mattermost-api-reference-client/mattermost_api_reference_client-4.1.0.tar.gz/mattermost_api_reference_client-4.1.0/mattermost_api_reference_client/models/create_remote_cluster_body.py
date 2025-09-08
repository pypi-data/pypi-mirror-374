from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateRemoteClusterBody")


@_attrs_define
class CreateRemoteClusterBody:
    """
    Attributes:
        name (str):
        default_team_id (str):
        display_name (Union[Unset, str]):
        password (Union[Unset, str]): The password to use in the invite code. If empty,
            the server will generate one and it will be part
            of the response
    """

    name: str
    default_team_id: str
    display_name: Union[Unset, str] = UNSET
    password: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        default_team_id = self.default_team_id

        display_name = self.display_name

        password = self.password

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "default_team_id": default_team_id,
            }
        )
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if password is not UNSET:
            field_dict["password"] = password

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        default_team_id = d.pop("default_team_id")

        display_name = d.pop("display_name", UNSET)

        password = d.pop("password", UNSET)

        create_remote_cluster_body = cls(
            name=name,
            default_team_id=default_team_id,
            display_name=display_name,
            password=password,
        )

        create_remote_cluster_body.additional_properties = d
        return create_remote_cluster_body

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
