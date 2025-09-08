from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ConfigClusterSettings")


@_attrs_define
class ConfigClusterSettings:
    """
    Attributes:
        enable (Union[Unset, bool]):
        inter_node_listen_address (Union[Unset, str]):
        inter_node_urls (Union[Unset, list[str]]):
    """

    enable: Union[Unset, bool] = UNSET
    inter_node_listen_address: Union[Unset, str] = UNSET
    inter_node_urls: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enable = self.enable

        inter_node_listen_address = self.inter_node_listen_address

        inter_node_urls: Union[Unset, list[str]] = UNSET
        if not isinstance(self.inter_node_urls, Unset):
            inter_node_urls = self.inter_node_urls

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enable is not UNSET:
            field_dict["Enable"] = enable
        if inter_node_listen_address is not UNSET:
            field_dict["InterNodeListenAddress"] = inter_node_listen_address
        if inter_node_urls is not UNSET:
            field_dict["InterNodeUrls"] = inter_node_urls

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        enable = d.pop("Enable", UNSET)

        inter_node_listen_address = d.pop("InterNodeListenAddress", UNSET)

        inter_node_urls = cast(list[str], d.pop("InterNodeUrls", UNSET))

        config_cluster_settings = cls(
            enable=enable,
            inter_node_listen_address=inter_node_listen_address,
            inter_node_urls=inter_node_urls,
        )

        config_cluster_settings.additional_properties = d
        return config_cluster_settings

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
