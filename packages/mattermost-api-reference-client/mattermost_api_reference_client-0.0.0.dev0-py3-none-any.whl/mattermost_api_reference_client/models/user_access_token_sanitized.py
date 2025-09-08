from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UserAccessTokenSanitized")


@_attrs_define
class UserAccessTokenSanitized:
    """
    Attributes:
        id (Union[Unset, str]): Unique identifier for the token
        user_id (Union[Unset, str]): The user the token authenticates for
        description (Union[Unset, str]): A description of the token usage
        is_active (Union[Unset, bool]): Indicates whether the token is active
    """

    id: Union[Unset, str] = UNSET
    user_id: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    is_active: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        user_id = self.user_id

        description = self.description

        is_active = self.is_active

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if description is not UNSET:
            field_dict["description"] = description
        if is_active is not UNSET:
            field_dict["is_active"] = is_active

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        user_id = d.pop("user_id", UNSET)

        description = d.pop("description", UNSET)

        is_active = d.pop("is_active", UNSET)

        user_access_token_sanitized = cls(
            id=id,
            user_id=user_id,
            description=description,
            is_active=is_active,
        )

        user_access_token_sanitized.additional_properties = d
        return user_access_token_sanitized

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
