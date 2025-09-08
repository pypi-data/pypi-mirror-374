from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ConfigPasswordSettings")


@_attrs_define
class ConfigPasswordSettings:
    """
    Attributes:
        minimum_length (Union[Unset, int]):
        lowercase (Union[Unset, bool]):
        number (Union[Unset, bool]):
        uppercase (Union[Unset, bool]):
        symbol (Union[Unset, bool]):
    """

    minimum_length: Union[Unset, int] = UNSET
    lowercase: Union[Unset, bool] = UNSET
    number: Union[Unset, bool] = UNSET
    uppercase: Union[Unset, bool] = UNSET
    symbol: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        minimum_length = self.minimum_length

        lowercase = self.lowercase

        number = self.number

        uppercase = self.uppercase

        symbol = self.symbol

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if minimum_length is not UNSET:
            field_dict["MinimumLength"] = minimum_length
        if lowercase is not UNSET:
            field_dict["Lowercase"] = lowercase
        if number is not UNSET:
            field_dict["Number"] = number
        if uppercase is not UNSET:
            field_dict["Uppercase"] = uppercase
        if symbol is not UNSET:
            field_dict["Symbol"] = symbol

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        minimum_length = d.pop("MinimumLength", UNSET)

        lowercase = d.pop("Lowercase", UNSET)

        number = d.pop("Number", UNSET)

        uppercase = d.pop("Uppercase", UNSET)

        symbol = d.pop("Symbol", UNSET)

        config_password_settings = cls(
            minimum_length=minimum_length,
            lowercase=lowercase,
            number=number,
            uppercase=uppercase,
            symbol=symbol,
        )

        config_password_settings.additional_properties = d
        return config_password_settings

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
