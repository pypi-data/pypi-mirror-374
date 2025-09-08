from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ConfigComplianceSettings")


@_attrs_define
class ConfigComplianceSettings:
    """
    Attributes:
        enable (Union[Unset, bool]):
        directory (Union[Unset, str]):
        enable_daily (Union[Unset, bool]):
    """

    enable: Union[Unset, bool] = UNSET
    directory: Union[Unset, str] = UNSET
    enable_daily: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enable = self.enable

        directory = self.directory

        enable_daily = self.enable_daily

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enable is not UNSET:
            field_dict["Enable"] = enable
        if directory is not UNSET:
            field_dict["Directory"] = directory
        if enable_daily is not UNSET:
            field_dict["EnableDaily"] = enable_daily

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        enable = d.pop("Enable", UNSET)

        directory = d.pop("Directory", UNSET)

        enable_daily = d.pop("EnableDaily", UNSET)

        config_compliance_settings = cls(
            enable=enable,
            directory=directory,
            enable_daily=enable_daily,
        )

        config_compliance_settings.additional_properties = d
        return config_compliance_settings

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
