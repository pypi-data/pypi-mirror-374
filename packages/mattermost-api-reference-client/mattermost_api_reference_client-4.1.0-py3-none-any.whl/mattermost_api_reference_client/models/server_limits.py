from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ServerLimits")


@_attrs_define
class ServerLimits:
    """
    Attributes:
        max_users_limit (Union[Unset, int]): The maximum number of users allowed on server
        active_user_count (Union[Unset, int]): The number of active users in the server
    """

    max_users_limit: Union[Unset, int] = UNSET
    active_user_count: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        max_users_limit = self.max_users_limit

        active_user_count = self.active_user_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if max_users_limit is not UNSET:
            field_dict["maxUsersLimit"] = max_users_limit
        if active_user_count is not UNSET:
            field_dict["activeUserCount"] = active_user_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        max_users_limit = d.pop("maxUsersLimit", UNSET)

        active_user_count = d.pop("activeUserCount", UNSET)

        server_limits = cls(
            max_users_limit=max_users_limit,
            active_user_count=active_user_count,
        )

        server_limits.additional_properties = d
        return server_limits

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
