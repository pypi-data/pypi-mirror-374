from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OpenGraphVideosItem")


@_attrs_define
class OpenGraphVideosItem:
    """Video object used in OpenGraph metadata of a webpage

    Attributes:
        url (Union[Unset, str]):
        secure_url (Union[Unset, str]):
        type_ (Union[Unset, str]):
        width (Union[Unset, int]):
        height (Union[Unset, int]):
    """

    url: Union[Unset, str] = UNSET
    secure_url: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    width: Union[Unset, int] = UNSET
    height: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        secure_url = self.secure_url

        type_ = self.type_

        width = self.width

        height = self.height

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if url is not UNSET:
            field_dict["url"] = url
        if secure_url is not UNSET:
            field_dict["secure_url"] = secure_url
        if type_ is not UNSET:
            field_dict["type"] = type_
        if width is not UNSET:
            field_dict["width"] = width
        if height is not UNSET:
            field_dict["height"] = height

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        url = d.pop("url", UNSET)

        secure_url = d.pop("secure_url", UNSET)

        type_ = d.pop("type", UNSET)

        width = d.pop("width", UNSET)

        height = d.pop("height", UNSET)

        open_graph_videos_item = cls(
            url=url,
            secure_url=secure_url,
            type_=type_,
            width=width,
            height=height,
        )

        open_graph_videos_item.additional_properties = d
        return open_graph_videos_item

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
