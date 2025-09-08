from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SystemStatusResponse")


@_attrs_define
class SystemStatusResponse:
    """
    Attributes:
        android_latest_version (Union[Unset, str]): Latest Android version supported
        android_min_version (Union[Unset, str]): Minimum Android version supported
        desktop_latest_version (Union[Unset, str]): Latest desktop version supported
        desktop_min_version (Union[Unset, str]): Minimum desktop version supported
        ios_latest_version (Union[Unset, str]): Latest iOS version supported
        ios_min_version (Union[Unset, str]): Minimum iOS version supported
        database_status (Union[Unset, str]): Status of database ("OK" or "UNHEALTHY"). Included when get_server_status
            parameter set.
        filestore_status (Union[Unset, str]): Status of filestore ("OK" or "UNHEALTHY"). Included when get_server_status
            parameter set.
        status (Union[Unset, str]): Status of server ("OK" or "UNHEALTHY"). Included when get_server_status parameter
            set.
        can_receive_notifications (Union[Unset, str]): Whether the device id provided can receive notifications ("true",
            "false" or "unknown"). Included when device_id parameter set.
    """

    android_latest_version: Union[Unset, str] = UNSET
    android_min_version: Union[Unset, str] = UNSET
    desktop_latest_version: Union[Unset, str] = UNSET
    desktop_min_version: Union[Unset, str] = UNSET
    ios_latest_version: Union[Unset, str] = UNSET
    ios_min_version: Union[Unset, str] = UNSET
    database_status: Union[Unset, str] = UNSET
    filestore_status: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    can_receive_notifications: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        android_latest_version = self.android_latest_version

        android_min_version = self.android_min_version

        desktop_latest_version = self.desktop_latest_version

        desktop_min_version = self.desktop_min_version

        ios_latest_version = self.ios_latest_version

        ios_min_version = self.ios_min_version

        database_status = self.database_status

        filestore_status = self.filestore_status

        status = self.status

        can_receive_notifications = self.can_receive_notifications

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if android_latest_version is not UNSET:
            field_dict["AndroidLatestVersion"] = android_latest_version
        if android_min_version is not UNSET:
            field_dict["AndroidMinVersion"] = android_min_version
        if desktop_latest_version is not UNSET:
            field_dict["DesktopLatestVersion"] = desktop_latest_version
        if desktop_min_version is not UNSET:
            field_dict["DesktopMinVersion"] = desktop_min_version
        if ios_latest_version is not UNSET:
            field_dict["IosLatestVersion"] = ios_latest_version
        if ios_min_version is not UNSET:
            field_dict["IosMinVersion"] = ios_min_version
        if database_status is not UNSET:
            field_dict["database_status"] = database_status
        if filestore_status is not UNSET:
            field_dict["filestore_status"] = filestore_status
        if status is not UNSET:
            field_dict["status"] = status
        if can_receive_notifications is not UNSET:
            field_dict["CanReceiveNotifications"] = can_receive_notifications

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        android_latest_version = d.pop("AndroidLatestVersion", UNSET)

        android_min_version = d.pop("AndroidMinVersion", UNSET)

        desktop_latest_version = d.pop("DesktopLatestVersion", UNSET)

        desktop_min_version = d.pop("DesktopMinVersion", UNSET)

        ios_latest_version = d.pop("IosLatestVersion", UNSET)

        ios_min_version = d.pop("IosMinVersion", UNSET)

        database_status = d.pop("database_status", UNSET)

        filestore_status = d.pop("filestore_status", UNSET)

        status = d.pop("status", UNSET)

        can_receive_notifications = d.pop("CanReceiveNotifications", UNSET)

        system_status_response = cls(
            android_latest_version=android_latest_version,
            android_min_version=android_min_version,
            desktop_latest_version=desktop_latest_version,
            desktop_min_version=desktop_min_version,
            ios_latest_version=ios_latest_version,
            ios_min_version=ios_min_version,
            database_status=database_status,
            filestore_status=filestore_status,
            status=status,
            can_receive_notifications=can_receive_notifications,
        )

        system_status_response.additional_properties = d
        return system_status_response

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
