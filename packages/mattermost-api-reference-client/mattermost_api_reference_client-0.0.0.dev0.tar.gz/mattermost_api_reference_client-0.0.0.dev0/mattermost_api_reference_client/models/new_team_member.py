from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="NewTeamMember")


@_attrs_define
class NewTeamMember:
    """
    Attributes:
        id (Union[Unset, str]): The user's ID.
        username (Union[Unset, str]):
        first_name (Union[Unset, str]):
        last_name (Union[Unset, str]):
        nickname (Union[Unset, str]):
        position (Union[Unset, str]): The user's position field value.
        create_at (Union[Unset, int]): The creation timestamp of the team member record.
    """

    id: Union[Unset, str] = UNSET
    username: Union[Unset, str] = UNSET
    first_name: Union[Unset, str] = UNSET
    last_name: Union[Unset, str] = UNSET
    nickname: Union[Unset, str] = UNSET
    position: Union[Unset, str] = UNSET
    create_at: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        username = self.username

        first_name = self.first_name

        last_name = self.last_name

        nickname = self.nickname

        position = self.position

        create_at = self.create_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if username is not UNSET:
            field_dict["username"] = username
        if first_name is not UNSET:
            field_dict["first_name"] = first_name
        if last_name is not UNSET:
            field_dict["last_name"] = last_name
        if nickname is not UNSET:
            field_dict["nickname"] = nickname
        if position is not UNSET:
            field_dict["position"] = position
        if create_at is not UNSET:
            field_dict["create_at"] = create_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        username = d.pop("username", UNSET)

        first_name = d.pop("first_name", UNSET)

        last_name = d.pop("last_name", UNSET)

        nickname = d.pop("nickname", UNSET)

        position = d.pop("position", UNSET)

        create_at = d.pop("create_at", UNSET)

        new_team_member = cls(
            id=id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            nickname=nickname,
            position=position,
            create_at=create_at,
        )

        new_team_member.additional_properties = d
        return new_team_member

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
