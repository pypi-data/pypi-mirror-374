from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Scheme")


@_attrs_define
class Scheme:
    """
    Attributes:
        id (Union[Unset, str]): The unique identifier of the scheme.
        name (Union[Unset, str]): The human readable name for the scheme.
        description (Union[Unset, str]): A human readable description of the scheme.
        create_at (Union[Unset, int]): The time at which the scheme was created.
        update_at (Union[Unset, int]): The time at which the scheme was last updated.
        delete_at (Union[Unset, int]): The time at which the scheme was deleted.
        scope (Union[Unset, str]): The scope to which this scheme can be applied, either "team" or "channel".
        default_team_admin_role (Union[Unset, str]): The id of the default team admin role for this scheme.
        default_team_user_role (Union[Unset, str]): The id of the default team user role for this scheme.
        default_channel_admin_role (Union[Unset, str]): The id of the default channel admin role for this scheme.
        default_channel_user_role (Union[Unset, str]): The id of the default channel user role for this scheme.
    """

    id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    create_at: Union[Unset, int] = UNSET
    update_at: Union[Unset, int] = UNSET
    delete_at: Union[Unset, int] = UNSET
    scope: Union[Unset, str] = UNSET
    default_team_admin_role: Union[Unset, str] = UNSET
    default_team_user_role: Union[Unset, str] = UNSET
    default_channel_admin_role: Union[Unset, str] = UNSET
    default_channel_user_role: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        description = self.description

        create_at = self.create_at

        update_at = self.update_at

        delete_at = self.delete_at

        scope = self.scope

        default_team_admin_role = self.default_team_admin_role

        default_team_user_role = self.default_team_user_role

        default_channel_admin_role = self.default_channel_admin_role

        default_channel_user_role = self.default_channel_user_role

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if create_at is not UNSET:
            field_dict["create_at"] = create_at
        if update_at is not UNSET:
            field_dict["update_at"] = update_at
        if delete_at is not UNSET:
            field_dict["delete_at"] = delete_at
        if scope is not UNSET:
            field_dict["scope"] = scope
        if default_team_admin_role is not UNSET:
            field_dict["default_team_admin_role"] = default_team_admin_role
        if default_team_user_role is not UNSET:
            field_dict["default_team_user_role"] = default_team_user_role
        if default_channel_admin_role is not UNSET:
            field_dict["default_channel_admin_role"] = default_channel_admin_role
        if default_channel_user_role is not UNSET:
            field_dict["default_channel_user_role"] = default_channel_user_role

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        create_at = d.pop("create_at", UNSET)

        update_at = d.pop("update_at", UNSET)

        delete_at = d.pop("delete_at", UNSET)

        scope = d.pop("scope", UNSET)

        default_team_admin_role = d.pop("default_team_admin_role", UNSET)

        default_team_user_role = d.pop("default_team_user_role", UNSET)

        default_channel_admin_role = d.pop("default_channel_admin_role", UNSET)

        default_channel_user_role = d.pop("default_channel_user_role", UNSET)

        scheme = cls(
            id=id,
            name=name,
            description=description,
            create_at=create_at,
            update_at=update_at,
            delete_at=delete_at,
            scope=scope,
            default_team_admin_role=default_team_admin_role,
            default_team_user_role=default_team_user_role,
            default_channel_admin_role=default_channel_admin_role,
            default_channel_user_role=default_channel_user_role,
        )

        scheme.additional_properties = d
        return scheme

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
