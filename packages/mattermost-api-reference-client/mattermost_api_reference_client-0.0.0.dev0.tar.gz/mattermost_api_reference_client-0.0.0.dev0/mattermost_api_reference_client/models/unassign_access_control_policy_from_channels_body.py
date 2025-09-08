from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UnassignAccessControlPolicyFromChannelsBody")


@_attrs_define
class UnassignAccessControlPolicyFromChannelsBody:
    """
    Attributes:
        channel_ids (Union[Unset, list[str]]): The IDs of the channels to unassign the policy from.
    """

    channel_ids: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        channel_ids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.channel_ids, Unset):
            channel_ids = self.channel_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if channel_ids is not UNSET:
            field_dict["channel_ids"] = channel_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        channel_ids = cast(list[str], d.pop("channel_ids", UNSET))

        unassign_access_control_policy_from_channels_body = cls(
            channel_ids=channel_ids,
        )

        unassign_access_control_policy_from_channels_body.additional_properties = d
        return unassign_access_control_policy_from_channels_body

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
