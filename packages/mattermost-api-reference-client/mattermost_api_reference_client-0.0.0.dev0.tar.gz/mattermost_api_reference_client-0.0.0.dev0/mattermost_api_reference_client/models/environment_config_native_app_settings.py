from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EnvironmentConfigNativeAppSettings")


@_attrs_define
class EnvironmentConfigNativeAppSettings:
    """
    Attributes:
        app_download_link (Union[Unset, bool]):
        android_app_download_link (Union[Unset, bool]):
        ios_app_download_link (Union[Unset, bool]):
    """

    app_download_link: Union[Unset, bool] = UNSET
    android_app_download_link: Union[Unset, bool] = UNSET
    ios_app_download_link: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        app_download_link = self.app_download_link

        android_app_download_link = self.android_app_download_link

        ios_app_download_link = self.ios_app_download_link

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if app_download_link is not UNSET:
            field_dict["AppDownloadLink"] = app_download_link
        if android_app_download_link is not UNSET:
            field_dict["AndroidAppDownloadLink"] = android_app_download_link
        if ios_app_download_link is not UNSET:
            field_dict["IosAppDownloadLink"] = ios_app_download_link

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        app_download_link = d.pop("AppDownloadLink", UNSET)

        android_app_download_link = d.pop("AndroidAppDownloadLink", UNSET)

        ios_app_download_link = d.pop("IosAppDownloadLink", UNSET)

        environment_config_native_app_settings = cls(
            app_download_link=app_download_link,
            android_app_download_link=android_app_download_link,
            ios_app_download_link=ios_app_download_link,
        )

        environment_config_native_app_settings.additional_properties = d
        return environment_config_native_app_settings

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
