from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetGroupStatsResponse200")


@_attrs_define
class GetGroupStatsResponse200:
    """
    Attributes:
        group_id (Union[Unset, str]):
        total_member_count (Union[Unset, int]):
    """

    group_id: Union[Unset, str] = UNSET
    total_member_count: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        group_id = self.group_id

        total_member_count = self.total_member_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if group_id is not UNSET:
            field_dict["group_id"] = group_id
        if total_member_count is not UNSET:
            field_dict["total_member_count"] = total_member_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        group_id = d.pop("group_id", UNSET)

        total_member_count = d.pop("total_member_count", UNSET)

        get_group_stats_response_200 = cls(
            group_id=group_id,
            total_member_count=total_member_count,
        )

        get_group_stats_response_200.additional_properties = d
        return get_group_stats_response_200

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
