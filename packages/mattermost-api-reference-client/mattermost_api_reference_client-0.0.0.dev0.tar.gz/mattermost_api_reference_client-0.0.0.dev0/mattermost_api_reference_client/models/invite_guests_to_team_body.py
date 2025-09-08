from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="InviteGuestsToTeamBody")


@_attrs_define
class InviteGuestsToTeamBody:
    """
    Attributes:
        emails (list[str]): List of emails
        channels (list[str]): List of channel ids
        message (Union[Unset, str]): Message to include in the invite
    """

    emails: list[str]
    channels: list[str]
    message: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        emails = self.emails

        channels = self.channels

        message = self.message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "emails": emails,
                "channels": channels,
            }
        )
        if message is not UNSET:
            field_dict["message"] = message

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        emails = cast(list[str], d.pop("emails"))

        channels = cast(list[str], d.pop("channels"))

        message = d.pop("message", UNSET)

        invite_guests_to_team_body = cls(
            emails=emails,
            channels=channels,
            message=message,
        )

        invite_guests_to_team_body.additional_properties = d
        return invite_guests_to_team_body

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
