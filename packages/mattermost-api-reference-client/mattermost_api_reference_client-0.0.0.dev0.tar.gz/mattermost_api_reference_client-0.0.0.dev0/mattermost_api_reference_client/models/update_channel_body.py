from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateChannelBody")


@_attrs_define
class UpdateChannelBody:
    """
    Attributes:
        id (str): The channel's id, not updatable
        name (Union[Unset, str]): The unique handle for the channel, will be present in the channel URL
        display_name (Union[Unset, str]): The non-unique UI name for the channel
        purpose (Union[Unset, str]): A short description of the purpose of the channel
        header (Union[Unset, str]): Markdown-formatted text to display in the header of the channel
    """

    id: str
    name: Union[Unset, str] = UNSET
    display_name: Union[Unset, str] = UNSET
    purpose: Union[Unset, str] = UNSET
    header: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        display_name = self.display_name

        purpose = self.purpose

        header = self.header

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if purpose is not UNSET:
            field_dict["purpose"] = purpose
        if header is not UNSET:
            field_dict["header"] = header

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name", UNSET)

        display_name = d.pop("display_name", UNSET)

        purpose = d.pop("purpose", UNSET)

        header = d.pop("header", UNSET)

        update_channel_body = cls(
            id=id,
            name=name,
            display_name=display_name,
            purpose=purpose,
            header=header,
        )

        update_channel_body.additional_properties = d
        return update_channel_body

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
