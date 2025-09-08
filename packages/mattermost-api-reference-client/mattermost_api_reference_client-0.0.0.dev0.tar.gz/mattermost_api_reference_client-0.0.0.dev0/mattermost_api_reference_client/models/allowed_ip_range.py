from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AllowedIPRange")


@_attrs_define
class AllowedIPRange:
    """
    Attributes:
        cidr_block (Union[Unset, str]): An IP address range in CIDR notation
        description (Union[Unset, str]): A description for the CIDRBlock
    """

    cidr_block: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cidr_block = self.cidr_block

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cidr_block is not UNSET:
            field_dict["CIDRBlock"] = cidr_block
        if description is not UNSET:
            field_dict["Description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        cidr_block = d.pop("CIDRBlock", UNSET)

        description = d.pop("Description", UNSET)

        allowed_ip_range = cls(
            cidr_block=cidr_block,
            description=description,
        )

        allowed_ip_range.additional_properties = d
        return allowed_ip_range

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
