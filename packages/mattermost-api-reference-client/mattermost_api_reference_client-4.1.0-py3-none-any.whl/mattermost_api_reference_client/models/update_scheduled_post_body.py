from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="UpdateScheduledPostBody")


@_attrs_define
class UpdateScheduledPostBody:
    """
    Attributes:
        id (str): ID of the scheduled post to update
        channel_id (str): The channel ID to post in
        user_id (str): The current user ID
        scheduled_at (int): UNIX timestamp in milliseconds of the time when the scheduled post should be sent
        message (str): The message contents, can be formatted with Markdown
    """

    id: str
    channel_id: str
    user_id: str
    scheduled_at: int
    message: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        channel_id = self.channel_id

        user_id = self.user_id

        scheduled_at = self.scheduled_at

        message = self.message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "channel_id": channel_id,
                "user_id": user_id,
                "scheduled_at": scheduled_at,
                "message": message,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        channel_id = d.pop("channel_id")

        user_id = d.pop("user_id")

        scheduled_at = d.pop("scheduled_at")

        message = d.pop("message")

        update_scheduled_post_body = cls(
            id=id,
            channel_id=channel_id,
            user_id=user_id,
            scheduled_at=scheduled_at,
            message=message,
        )

        update_scheduled_post_body.additional_properties = d
        return update_scheduled_post_body

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
