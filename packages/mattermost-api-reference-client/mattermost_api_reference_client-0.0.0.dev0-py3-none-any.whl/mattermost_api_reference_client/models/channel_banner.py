from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ChannelBanner")


@_attrs_define
class ChannelBanner:
    """
    Attributes:
        enabled (Union[Unset, bool]): enabled indicates whether the channel banner is enabled or not
        text (Union[Unset, str]): text is the actual text that renders in the channel banner. Markdown is supported.
        background_color (Union[Unset, str]): background_color is the HEX color code for the banner's backgroubd
    """

    enabled: Union[Unset, bool] = UNSET
    text: Union[Unset, str] = UNSET
    background_color: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enabled = self.enabled

        text = self.text

        background_color = self.background_color

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if text is not UNSET:
            field_dict["text"] = text
        if background_color is not UNSET:
            field_dict["background_color"] = background_color

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        enabled = d.pop("enabled", UNSET)

        text = d.pop("text", UNSET)

        background_color = d.pop("background_color", UNSET)

        channel_banner = cls(
            enabled=enabled,
            text=text,
            background_color=background_color,
        )

        channel_banner.additional_properties = d
        return channel_banner

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
