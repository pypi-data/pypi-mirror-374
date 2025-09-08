from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="TeamMember")


@_attrs_define
class TeamMember:
    """
    Attributes:
        team_id (Union[Unset, str]): The ID of the team this member belongs to.
        user_id (Union[Unset, str]): The ID of the user this member relates to.
        roles (Union[Unset, str]): The complete list of roles assigned to this team member, as a space-separated list of
            role names, including any roles granted implicitly through permissions schemes.
        delete_at (Union[Unset, int]): The time in milliseconds that this team member was deleted.
        scheme_user (Union[Unset, bool]): Whether this team member holds the default user role defined by the team's
            permissions scheme.
        scheme_admin (Union[Unset, bool]): Whether this team member holds the default admin role defined by the team's
            permissions scheme.
        explicit_roles (Union[Unset, str]): The list of roles explicitly assigned to this team member, as a space
            separated list of role names. This list does *not* include any roles granted implicitly through permissions
            schemes.
    """

    team_id: Union[Unset, str] = UNSET
    user_id: Union[Unset, str] = UNSET
    roles: Union[Unset, str] = UNSET
    delete_at: Union[Unset, int] = UNSET
    scheme_user: Union[Unset, bool] = UNSET
    scheme_admin: Union[Unset, bool] = UNSET
    explicit_roles: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        team_id = self.team_id

        user_id = self.user_id

        roles = self.roles

        delete_at = self.delete_at

        scheme_user = self.scheme_user

        scheme_admin = self.scheme_admin

        explicit_roles = self.explicit_roles

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if team_id is not UNSET:
            field_dict["team_id"] = team_id
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if roles is not UNSET:
            field_dict["roles"] = roles
        if delete_at is not UNSET:
            field_dict["delete_at"] = delete_at
        if scheme_user is not UNSET:
            field_dict["scheme_user"] = scheme_user
        if scheme_admin is not UNSET:
            field_dict["scheme_admin"] = scheme_admin
        if explicit_roles is not UNSET:
            field_dict["explicit_roles"] = explicit_roles

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        team_id = d.pop("team_id", UNSET)

        user_id = d.pop("user_id", UNSET)

        roles = d.pop("roles", UNSET)

        delete_at = d.pop("delete_at", UNSET)

        scheme_user = d.pop("scheme_user", UNSET)

        scheme_admin = d.pop("scheme_admin", UNSET)

        explicit_roles = d.pop("explicit_roles", UNSET)

        team_member = cls(
            team_id=team_id,
            user_id=user_id,
            roles=roles,
            delete_at=delete_at,
            scheme_user=scheme_user,
            scheme_admin=scheme_admin,
            explicit_roles=explicit_roles,
        )

        team_member.additional_properties = d
        return team_member

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
