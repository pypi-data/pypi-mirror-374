from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ChannelModeratedRolesPatch")


@_attrs_define
class ChannelModeratedRolesPatch:
    """
    Attributes:
        guests (Union[Unset, bool]):
        members (Union[Unset, bool]):
    """

    guests: Union[Unset, bool] = UNSET
    members: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        guests = self.guests

        members = self.members

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if guests is not UNSET:
            field_dict["guests"] = guests
        if members is not UNSET:
            field_dict["members"] = members

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        guests = d.pop("guests", UNSET)

        members = d.pop("members", UNSET)

        channel_moderated_roles_patch = cls(
            guests=guests,
            members=members,
        )

        channel_moderated_roles_patch.additional_properties = d
        return channel_moderated_roles_patch

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
