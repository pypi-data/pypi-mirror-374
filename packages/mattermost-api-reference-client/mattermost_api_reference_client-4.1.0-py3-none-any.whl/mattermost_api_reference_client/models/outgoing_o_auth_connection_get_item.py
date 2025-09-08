from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OutgoingOAuthConnectionGetItem")


@_attrs_define
class OutgoingOAuthConnectionGetItem:
    """
    Attributes:
        id (Union[Unset, str]): The unique identifier for the outgoing OAuth connection.
        name (Union[Unset, str]): The name of the outgoing OAuth connection.
        create_at (Union[Unset, int]): The time in milliseconds the outgoing OAuth connection was created.
        update_at (Union[Unset, int]): The time in milliseconds the outgoing OAuth connection was last updated.
        grant_type (Union[Unset, str]): The grant type of the outgoing OAuth connection.
        audiences (Union[Unset, str]): The audiences of the outgoing OAuth connection.
    """

    id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    create_at: Union[Unset, int] = UNSET
    update_at: Union[Unset, int] = UNSET
    grant_type: Union[Unset, str] = UNSET
    audiences: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        create_at = self.create_at

        update_at = self.update_at

        grant_type = self.grant_type

        audiences = self.audiences

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if create_at is not UNSET:
            field_dict["create_at"] = create_at
        if update_at is not UNSET:
            field_dict["update_at"] = update_at
        if grant_type is not UNSET:
            field_dict["grant_type"] = grant_type
        if audiences is not UNSET:
            field_dict["audiences"] = audiences

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        create_at = d.pop("create_at", UNSET)

        update_at = d.pop("update_at", UNSET)

        grant_type = d.pop("grant_type", UNSET)

        audiences = d.pop("audiences", UNSET)

        outgoing_o_auth_connection_get_item = cls(
            id=id,
            name=name,
            create_at=create_at,
            update_at=update_at,
            grant_type=grant_type,
            audiences=audiences,
        )

        outgoing_o_auth_connection_get_item.additional_properties = d
        return outgoing_o_auth_connection_get_item

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
