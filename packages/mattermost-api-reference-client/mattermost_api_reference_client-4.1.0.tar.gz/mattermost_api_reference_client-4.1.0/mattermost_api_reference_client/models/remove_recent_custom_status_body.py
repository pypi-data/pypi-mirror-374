from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="RemoveRecentCustomStatusBody")


@_attrs_define
class RemoveRecentCustomStatusBody:
    """
    Attributes:
        emoji (str): Any emoji
        text (str): Any custom status text
        duration (str): Duration of custom status, can be `thirty_minutes`, `one_hour`, `four_hours`, `today`,
            `this_week` or `date_and_time`
        expires_at (str): The time at which custom status should be expired. It should be in ISO format.
    """

    emoji: str
    text: str
    duration: str
    expires_at: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        emoji = self.emoji

        text = self.text

        duration = self.duration

        expires_at = self.expires_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "emoji": emoji,
                "text": text,
                "duration": duration,
                "expires_at": expires_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        emoji = d.pop("emoji")

        text = d.pop("text")

        duration = d.pop("duration")

        expires_at = d.pop("expires_at")

        remove_recent_custom_status_body = cls(
            emoji=emoji,
            text=text,
            duration=duration,
            expires_at=expires_at,
        )

        remove_recent_custom_status_body.additional_properties = d
        return remove_recent_custom_status_body

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
