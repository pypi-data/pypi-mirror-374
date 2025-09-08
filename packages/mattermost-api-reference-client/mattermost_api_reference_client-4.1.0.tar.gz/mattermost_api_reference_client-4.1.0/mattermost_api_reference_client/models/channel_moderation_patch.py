from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.channel_moderated_roles_patch import ChannelModeratedRolesPatch


T = TypeVar("T", bound="ChannelModerationPatch")


@_attrs_define
class ChannelModerationPatch:
    """
    Attributes:
        name (Union[Unset, str]):
        roles (Union[Unset, ChannelModeratedRolesPatch]):
    """

    name: Union[Unset, str] = UNSET
    roles: Union[Unset, "ChannelModeratedRolesPatch"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        roles: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.roles, Unset):
            roles = self.roles.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if roles is not UNSET:
            field_dict["roles"] = roles

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.channel_moderated_roles_patch import ChannelModeratedRolesPatch

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        _roles = d.pop("roles", UNSET)
        roles: Union[Unset, ChannelModeratedRolesPatch]
        if isinstance(_roles, Unset):
            roles = UNSET
        else:
            roles = ChannelModeratedRolesPatch.from_dict(_roles)

        channel_moderation_patch = cls(
            name=name,
            roles=roles,
        )

        channel_moderation_patch.additional_properties = d
        return channel_moderation_patch

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
