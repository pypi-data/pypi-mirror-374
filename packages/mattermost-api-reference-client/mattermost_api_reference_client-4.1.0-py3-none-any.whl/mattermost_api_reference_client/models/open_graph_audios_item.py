from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OpenGraphAudiosItem")


@_attrs_define
class OpenGraphAudiosItem:
    """Audio object used in OpenGraph metadata of a webpage

    Attributes:
        url (Union[Unset, str]):
        secure_url (Union[Unset, str]):
        type_ (Union[Unset, str]):
    """

    url: Union[Unset, str] = UNSET
    secure_url: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        secure_url = self.secure_url

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if url is not UNSET:
            field_dict["url"] = url
        if secure_url is not UNSET:
            field_dict["secure_url"] = secure_url
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        url = d.pop("url", UNSET)

        secure_url = d.pop("secure_url", UNSET)

        type_ = d.pop("type", UNSET)

        open_graph_audios_item = cls(
            url=url,
            secure_url=secure_url,
            type_=type_,
        )

        open_graph_audios_item.additional_properties = d
        return open_graph_audios_item

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
