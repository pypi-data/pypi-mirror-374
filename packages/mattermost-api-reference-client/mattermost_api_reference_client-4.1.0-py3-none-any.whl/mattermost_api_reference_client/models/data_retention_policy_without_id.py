from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DataRetentionPolicyWithoutId")


@_attrs_define
class DataRetentionPolicyWithoutId:
    """
    Attributes:
        display_name (Union[Unset, str]): The display name for this retention policy.
        post_duration (Union[Unset, int]): The number of days a message will be retained before being deleted by this
            policy. If this value is less than 0, the policy has infinite retention (i.e. messages are never deleted).
    """

    display_name: Union[Unset, str] = UNSET
    post_duration: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        display_name = self.display_name

        post_duration = self.post_duration

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if post_duration is not UNSET:
            field_dict["post_duration"] = post_duration

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        display_name = d.pop("display_name", UNSET)

        post_duration = d.pop("post_duration", UNSET)

        data_retention_policy_without_id = cls(
            display_name=display_name,
            post_duration=post_duration,
        )

        data_retention_policy_without_id.additional_properties = d
        return data_retention_policy_without_id

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
