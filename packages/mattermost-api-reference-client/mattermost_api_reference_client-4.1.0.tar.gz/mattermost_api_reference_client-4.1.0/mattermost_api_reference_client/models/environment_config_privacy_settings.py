from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EnvironmentConfigPrivacySettings")


@_attrs_define
class EnvironmentConfigPrivacySettings:
    """
    Attributes:
        show_email_address (Union[Unset, bool]):
        show_full_name (Union[Unset, bool]):
    """

    show_email_address: Union[Unset, bool] = UNSET
    show_full_name: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        show_email_address = self.show_email_address

        show_full_name = self.show_full_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if show_email_address is not UNSET:
            field_dict["ShowEmailAddress"] = show_email_address
        if show_full_name is not UNSET:
            field_dict["ShowFullName"] = show_full_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        show_email_address = d.pop("ShowEmailAddress", UNSET)

        show_full_name = d.pop("ShowFullName", UNSET)

        environment_config_privacy_settings = cls(
            show_email_address=show_email_address,
            show_full_name=show_full_name,
        )

        environment_config_privacy_settings.additional_properties = d
        return environment_config_privacy_settings

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
