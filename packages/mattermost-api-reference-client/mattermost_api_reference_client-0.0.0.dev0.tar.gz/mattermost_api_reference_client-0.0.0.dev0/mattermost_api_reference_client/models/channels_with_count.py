from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.channel_with_team_data import ChannelWithTeamData


T = TypeVar("T", bound="ChannelsWithCount")


@_attrs_define
class ChannelsWithCount:
    """
    Attributes:
        channels (Union[Unset, list['ChannelWithTeamData']]):
        total_count (Union[Unset, int]): The total number of channels.
    """

    channels: Union[Unset, list["ChannelWithTeamData"]] = UNSET
    total_count: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        channels: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.channels, Unset):
            channels = []
            for componentsschemas_channel_list_with_team_data_item_data in self.channels:
                componentsschemas_channel_list_with_team_data_item = (
                    componentsschemas_channel_list_with_team_data_item_data.to_dict()
                )
                channels.append(componentsschemas_channel_list_with_team_data_item)

        total_count = self.total_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if channels is not UNSET:
            field_dict["channels"] = channels
        if total_count is not UNSET:
            field_dict["total_count"] = total_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.channel_with_team_data import ChannelWithTeamData

        d = dict(src_dict)
        channels = []
        _channels = d.pop("channels", UNSET)
        for componentsschemas_channel_list_with_team_data_item_data in _channels or []:
            componentsschemas_channel_list_with_team_data_item = ChannelWithTeamData.from_dict(
                componentsschemas_channel_list_with_team_data_item_data
            )

            channels.append(componentsschemas_channel_list_with_team_data_item)

        total_count = d.pop("total_count", UNSET)

        channels_with_count = cls(
            channels=channels,
            total_count=total_count,
        )

        channels_with_count.additional_properties = d
        return channels_with_count

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
