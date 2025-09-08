from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ViewChannelBody")


@_attrs_define
class ViewChannelBody:
    """
    Attributes:
        channel_id (str): The channel ID that is being viewed. Use a blank string to indicate that all channels have
            lost focus.
        prev_channel_id (Union[Unset, str]): The channel ID of the previous channel, used when switching channels.
            Providing this ID will cause push notifications to clear on the channel being switched to.
    """

    channel_id: str
    prev_channel_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        channel_id = self.channel_id

        prev_channel_id = self.prev_channel_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "channel_id": channel_id,
            }
        )
        if prev_channel_id is not UNSET:
            field_dict["prev_channel_id"] = prev_channel_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        channel_id = d.pop("channel_id")

        prev_channel_id = d.pop("prev_channel_id", UNSET)

        view_channel_body = cls(
            channel_id=channel_id,
            prev_channel_id=prev_channel_id,
        )

        view_channel_body.additional_properties = d
        return view_channel_body

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
