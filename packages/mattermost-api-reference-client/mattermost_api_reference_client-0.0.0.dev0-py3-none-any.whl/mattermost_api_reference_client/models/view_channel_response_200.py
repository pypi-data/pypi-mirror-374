from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.view_channel_response_200_last_viewed_at_times import ViewChannelResponse200LastViewedAtTimes


T = TypeVar("T", bound="ViewChannelResponse200")


@_attrs_define
class ViewChannelResponse200:
    """
    Attributes:
        status (Union[Unset, str]): Value should be "OK" if successful
        last_viewed_at_times (Union[Unset, ViewChannelResponse200LastViewedAtTimes]): A JSON object mapping channel IDs
            to the channel view times
    """

    status: Union[Unset, str] = UNSET
    last_viewed_at_times: Union[Unset, "ViewChannelResponse200LastViewedAtTimes"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status

        last_viewed_at_times: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.last_viewed_at_times, Unset):
            last_viewed_at_times = self.last_viewed_at_times.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if status is not UNSET:
            field_dict["status"] = status
        if last_viewed_at_times is not UNSET:
            field_dict["last_viewed_at_times"] = last_viewed_at_times

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.view_channel_response_200_last_viewed_at_times import ViewChannelResponse200LastViewedAtTimes

        d = dict(src_dict)
        status = d.pop("status", UNSET)

        _last_viewed_at_times = d.pop("last_viewed_at_times", UNSET)
        last_viewed_at_times: Union[Unset, ViewChannelResponse200LastViewedAtTimes]
        if isinstance(_last_viewed_at_times, Unset):
            last_viewed_at_times = UNSET
        else:
            last_viewed_at_times = ViewChannelResponse200LastViewedAtTimes.from_dict(_last_viewed_at_times)

        view_channel_response_200 = cls(
            status=status,
            last_viewed_at_times=last_viewed_at_times,
        )

        view_channel_response_200.additional_properties = d
        return view_channel_response_200

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
