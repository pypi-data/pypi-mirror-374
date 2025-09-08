from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SlackAttachmentField")


@_attrs_define
class SlackAttachmentField:
    """
    Attributes:
        title (Union[Unset, str]):
        value (Union[Unset, str]): The value of the attachment, set as string but capable with golang interface
        short (Union[Unset, bool]):
    """

    title: Union[Unset, str] = UNSET
    value: Union[Unset, str] = UNSET
    short: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        value = self.value

        short = self.short

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if title is not UNSET:
            field_dict["Title"] = title
        if value is not UNSET:
            field_dict["Value"] = value
        if short is not UNSET:
            field_dict["Short"] = short

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        title = d.pop("Title", UNSET)

        value = d.pop("Value", UNSET)

        short = d.pop("Short", UNSET)

        slack_attachment_field = cls(
            title=title,
            value=value,
            short=short,
        )

        slack_attachment_field.additional_properties = d
        return slack_attachment_field

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
