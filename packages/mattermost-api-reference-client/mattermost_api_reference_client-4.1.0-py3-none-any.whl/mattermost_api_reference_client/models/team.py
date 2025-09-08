from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Team")


@_attrs_define
class Team:
    """
    Attributes:
        id (Union[Unset, str]):
        create_at (Union[Unset, int]): The time in milliseconds a team was created
        update_at (Union[Unset, int]): The time in milliseconds a team was last updated
        delete_at (Union[Unset, int]): The time in milliseconds a team was deleted
        display_name (Union[Unset, str]):
        name (Union[Unset, str]):
        description (Union[Unset, str]):
        email (Union[Unset, str]):
        type_ (Union[Unset, str]):
        allowed_domains (Union[Unset, str]):
        invite_id (Union[Unset, str]):
        allow_open_invite (Union[Unset, bool]):
        policy_id (Union[Unset, str]): The data retention policy to which this team has been assigned. If no such policy
            exists, or the caller does not have the `sysconsole_read_compliance_data_retention` permission, this field will
            be null.
    """

    id: Union[Unset, str] = UNSET
    create_at: Union[Unset, int] = UNSET
    update_at: Union[Unset, int] = UNSET
    delete_at: Union[Unset, int] = UNSET
    display_name: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    allowed_domains: Union[Unset, str] = UNSET
    invite_id: Union[Unset, str] = UNSET
    allow_open_invite: Union[Unset, bool] = UNSET
    policy_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        create_at = self.create_at

        update_at = self.update_at

        delete_at = self.delete_at

        display_name = self.display_name

        name = self.name

        description = self.description

        email = self.email

        type_ = self.type_

        allowed_domains = self.allowed_domains

        invite_id = self.invite_id

        allow_open_invite = self.allow_open_invite

        policy_id = self.policy_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if create_at is not UNSET:
            field_dict["create_at"] = create_at
        if update_at is not UNSET:
            field_dict["update_at"] = update_at
        if delete_at is not UNSET:
            field_dict["delete_at"] = delete_at
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if email is not UNSET:
            field_dict["email"] = email
        if type_ is not UNSET:
            field_dict["type"] = type_
        if allowed_domains is not UNSET:
            field_dict["allowed_domains"] = allowed_domains
        if invite_id is not UNSET:
            field_dict["invite_id"] = invite_id
        if allow_open_invite is not UNSET:
            field_dict["allow_open_invite"] = allow_open_invite
        if policy_id is not UNSET:
            field_dict["policy_id"] = policy_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        create_at = d.pop("create_at", UNSET)

        update_at = d.pop("update_at", UNSET)

        delete_at = d.pop("delete_at", UNSET)

        display_name = d.pop("display_name", UNSET)

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        email = d.pop("email", UNSET)

        type_ = d.pop("type", UNSET)

        allowed_domains = d.pop("allowed_domains", UNSET)

        invite_id = d.pop("invite_id", UNSET)

        allow_open_invite = d.pop("allow_open_invite", UNSET)

        policy_id = d.pop("policy_id", UNSET)

        team = cls(
            id=id,
            create_at=create_at,
            update_at=update_at,
            delete_at=delete_at,
            display_name=display_name,
            name=name,
            description=description,
            email=email,
            type_=type_,
            allowed_domains=allowed_domains,
            invite_id=invite_id,
            allow_open_invite=allow_open_invite,
            policy_id=policy_id,
        )

        team.additional_properties = d
        return team

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
