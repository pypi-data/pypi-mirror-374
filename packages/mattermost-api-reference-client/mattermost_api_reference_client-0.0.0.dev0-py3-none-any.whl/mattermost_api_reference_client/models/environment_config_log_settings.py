from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EnvironmentConfigLogSettings")


@_attrs_define
class EnvironmentConfigLogSettings:
    """
    Attributes:
        enable_console (Union[Unset, bool]):
        console_level (Union[Unset, bool]):
        enable_file (Union[Unset, bool]):
        file_level (Union[Unset, bool]):
        file_location (Union[Unset, bool]):
        enable_webhook_debugging (Union[Unset, bool]):
        enable_diagnostics (Union[Unset, bool]):
    """

    enable_console: Union[Unset, bool] = UNSET
    console_level: Union[Unset, bool] = UNSET
    enable_file: Union[Unset, bool] = UNSET
    file_level: Union[Unset, bool] = UNSET
    file_location: Union[Unset, bool] = UNSET
    enable_webhook_debugging: Union[Unset, bool] = UNSET
    enable_diagnostics: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enable_console = self.enable_console

        console_level = self.console_level

        enable_file = self.enable_file

        file_level = self.file_level

        file_location = self.file_location

        enable_webhook_debugging = self.enable_webhook_debugging

        enable_diagnostics = self.enable_diagnostics

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enable_console is not UNSET:
            field_dict["EnableConsole"] = enable_console
        if console_level is not UNSET:
            field_dict["ConsoleLevel"] = console_level
        if enable_file is not UNSET:
            field_dict["EnableFile"] = enable_file
        if file_level is not UNSET:
            field_dict["FileLevel"] = file_level
        if file_location is not UNSET:
            field_dict["FileLocation"] = file_location
        if enable_webhook_debugging is not UNSET:
            field_dict["EnableWebhookDebugging"] = enable_webhook_debugging
        if enable_diagnostics is not UNSET:
            field_dict["EnableDiagnostics"] = enable_diagnostics

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        enable_console = d.pop("EnableConsole", UNSET)

        console_level = d.pop("ConsoleLevel", UNSET)

        enable_file = d.pop("EnableFile", UNSET)

        file_level = d.pop("FileLevel", UNSET)

        file_location = d.pop("FileLocation", UNSET)

        enable_webhook_debugging = d.pop("EnableWebhookDebugging", UNSET)

        enable_diagnostics = d.pop("EnableDiagnostics", UNSET)

        environment_config_log_settings = cls(
            enable_console=enable_console,
            console_level=console_level,
            enable_file=enable_file,
            file_level=file_level,
            file_location=file_location,
            enable_webhook_debugging=enable_webhook_debugging,
            enable_diagnostics=enable_diagnostics,
        )

        environment_config_log_settings.additional_properties = d
        return environment_config_log_settings

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
