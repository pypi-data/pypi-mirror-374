from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="UpdateOutgoingWebhookBody")


@_attrs_define
class UpdateOutgoingWebhookBody:
    """
    Attributes:
        id (str): Outgoing webhook GUID
        channel_id (str): The ID of a public channel or private group that receives the webhook payloads.
        display_name (str): The display name for this incoming webhook
        description (str): The description for this incoming webhook
    """

    id: str
    channel_id: str
    display_name: str
    description: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        channel_id = self.channel_id

        display_name = self.display_name

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "channel_id": channel_id,
                "display_name": display_name,
                "description": description,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        channel_id = d.pop("channel_id")

        display_name = d.pop("display_name")

        description = d.pop("description")

        update_outgoing_webhook_body = cls(
            id=id,
            channel_id=channel_id,
            display_name=display_name,
            description=description,
        )

        update_outgoing_webhook_body.additional_properties = d
        return update_outgoing_webhook_body

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
