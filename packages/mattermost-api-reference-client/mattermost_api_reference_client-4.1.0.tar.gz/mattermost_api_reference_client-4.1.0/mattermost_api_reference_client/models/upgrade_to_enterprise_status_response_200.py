from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpgradeToEnterpriseStatusResponse200")


@_attrs_define
class UpgradeToEnterpriseStatusResponse200:
    """
    Attributes:
        percentage (Union[Unset, int]): Current percentage of the upgrade
        error (Union[Unset, str]): Error happened during the upgrade
    """

    percentage: Union[Unset, int] = UNSET
    error: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        percentage = self.percentage

        error = self.error

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if percentage is not UNSET:
            field_dict["percentage"] = percentage
        if error is not UNSET:
            field_dict["error"] = error

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        percentage = d.pop("percentage", UNSET)

        error = d.pop("error", UNSET)

        upgrade_to_enterprise_status_response_200 = cls(
            percentage=percentage,
            error=error,
        )

        upgrade_to_enterprise_status_response_200.additional_properties = d
        return upgrade_to_enterprise_status_response_200

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
