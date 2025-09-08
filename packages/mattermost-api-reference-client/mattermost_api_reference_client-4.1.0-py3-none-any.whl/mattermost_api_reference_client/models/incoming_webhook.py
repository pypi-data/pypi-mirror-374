from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="IncomingWebhook")


@_attrs_define
class IncomingWebhook:
    """
    Attributes:
        id (Union[Unset, str]): The unique identifier for this incoming webhook
        create_at (Union[Unset, int]): The time in milliseconds a incoming webhook was created
        update_at (Union[Unset, int]): The time in milliseconds a incoming webhook was last updated
        delete_at (Union[Unset, int]): The time in milliseconds a incoming webhook was deleted
        channel_id (Union[Unset, str]): The ID of a public channel or private group that receives the webhook payloads
        description (Union[Unset, str]): The description for this incoming webhook
        display_name (Union[Unset, str]): The display name for this incoming webhook
    """

    id: Union[Unset, str] = UNSET
    create_at: Union[Unset, int] = UNSET
    update_at: Union[Unset, int] = UNSET
    delete_at: Union[Unset, int] = UNSET
    channel_id: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    display_name: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        create_at = self.create_at

        update_at = self.update_at

        delete_at = self.delete_at

        channel_id = self.channel_id

        description = self.description

        display_name = self.display_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if create_at is not UNSET:
            field_dict["create_at"] = create_at
        if update_at is not UNSET:
            field_dict["update_at"] = update_at
        if delete_at is not UNSET:
            field_dict["delete_at"] = delete_at
        if channel_id is not UNSET:
            field_dict["channel_id"] = channel_id
        if description is not UNSET:
            field_dict["description"] = description
        if display_name is not UNSET:
            field_dict["display_name"] = display_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        create_at = d.pop("create_at", UNSET)

        update_at = d.pop("update_at", UNSET)

        delete_at = d.pop("delete_at", UNSET)

        channel_id = d.pop("channel_id", UNSET)

        description = d.pop("description", UNSET)

        display_name = d.pop("display_name", UNSET)

        incoming_webhook = cls(
            id=id,
            create_at=create_at,
            update_at=update_at,
            delete_at=delete_at,
            channel_id=channel_id,
            description=description,
            display_name=display_name,
        )

        incoming_webhook.additional_properties = d
        return incoming_webhook

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
