from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EnvironmentConfigLocalizationSettings")


@_attrs_define
class EnvironmentConfigLocalizationSettings:
    """
    Attributes:
        default_server_locale (Union[Unset, bool]):
        default_client_locale (Union[Unset, bool]):
        available_locales (Union[Unset, bool]):
    """

    default_server_locale: Union[Unset, bool] = UNSET
    default_client_locale: Union[Unset, bool] = UNSET
    available_locales: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        default_server_locale = self.default_server_locale

        default_client_locale = self.default_client_locale

        available_locales = self.available_locales

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if default_server_locale is not UNSET:
            field_dict["DefaultServerLocale"] = default_server_locale
        if default_client_locale is not UNSET:
            field_dict["DefaultClientLocale"] = default_client_locale
        if available_locales is not UNSET:
            field_dict["AvailableLocales"] = available_locales

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        default_server_locale = d.pop("DefaultServerLocale", UNSET)

        default_client_locale = d.pop("DefaultClientLocale", UNSET)

        available_locales = d.pop("AvailableLocales", UNSET)

        environment_config_localization_settings = cls(
            default_server_locale=default_server_locale,
            default_client_locale=default_client_locale,
            available_locales=available_locales,
        )

        environment_config_localization_settings.additional_properties = d
        return environment_config_localization_settings

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
