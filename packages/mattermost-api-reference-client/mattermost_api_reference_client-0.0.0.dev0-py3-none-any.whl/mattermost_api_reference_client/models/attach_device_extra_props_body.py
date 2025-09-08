from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AttachDeviceExtraPropsBody")


@_attrs_define
class AttachDeviceExtraPropsBody:
    """
    Attributes:
        device_id (Union[Unset, str]): Mobile device id. For Android prefix the id with `android:` and Apple with
            `apple:`
        device_notification_disabled (Union[Unset, str]): Whether the mobile device has notifications disabled. Accepted
            values are "true" or "false".
        mobile_version (Union[Unset, str]): Mobile app version. The version must be parseable as a semver.
    """

    device_id: Union[Unset, str] = UNSET
    device_notification_disabled: Union[Unset, str] = UNSET
    mobile_version: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device_id = self.device_id

        device_notification_disabled = self.device_notification_disabled

        mobile_version = self.mobile_version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if device_id is not UNSET:
            field_dict["device_id"] = device_id
        if device_notification_disabled is not UNSET:
            field_dict["deviceNotificationDisabled"] = device_notification_disabled
        if mobile_version is not UNSET:
            field_dict["mobileVersion"] = mobile_version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        device_id = d.pop("device_id", UNSET)

        device_notification_disabled = d.pop("deviceNotificationDisabled", UNSET)

        mobile_version = d.pop("mobileVersion", UNSET)

        attach_device_extra_props_body = cls(
            device_id=device_id,
            device_notification_disabled=device_notification_disabled,
            mobile_version=mobile_version,
        )

        attach_device_extra_props_body.additional_properties = d
        return attach_device_extra_props_body

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
