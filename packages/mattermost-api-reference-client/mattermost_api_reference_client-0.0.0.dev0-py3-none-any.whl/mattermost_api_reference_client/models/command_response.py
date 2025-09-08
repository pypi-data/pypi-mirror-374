from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.slack_attachment import SlackAttachment


T = TypeVar("T", bound="CommandResponse")


@_attrs_define
class CommandResponse:
    """
    Attributes:
        response_type (Union[Unset, str]): The response type either in_channel or ephemeral
        text (Union[Unset, str]):
        username (Union[Unset, str]):
        icon_url (Union[Unset, str]):
        goto_location (Union[Unset, str]):
        attachments (Union[Unset, list['SlackAttachment']]):
    """

    response_type: Union[Unset, str] = UNSET
    text: Union[Unset, str] = UNSET
    username: Union[Unset, str] = UNSET
    icon_url: Union[Unset, str] = UNSET
    goto_location: Union[Unset, str] = UNSET
    attachments: Union[Unset, list["SlackAttachment"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        response_type = self.response_type

        text = self.text

        username = self.username

        icon_url = self.icon_url

        goto_location = self.goto_location

        attachments: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.attachments, Unset):
            attachments = []
            for attachments_item_data in self.attachments:
                attachments_item = attachments_item_data.to_dict()
                attachments.append(attachments_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if response_type is not UNSET:
            field_dict["ResponseType"] = response_type
        if text is not UNSET:
            field_dict["Text"] = text
        if username is not UNSET:
            field_dict["Username"] = username
        if icon_url is not UNSET:
            field_dict["IconURL"] = icon_url
        if goto_location is not UNSET:
            field_dict["GotoLocation"] = goto_location
        if attachments is not UNSET:
            field_dict["Attachments"] = attachments

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.slack_attachment import SlackAttachment

        d = dict(src_dict)
        response_type = d.pop("ResponseType", UNSET)

        text = d.pop("Text", UNSET)

        username = d.pop("Username", UNSET)

        icon_url = d.pop("IconURL", UNSET)

        goto_location = d.pop("GotoLocation", UNSET)

        attachments = []
        _attachments = d.pop("Attachments", UNSET)
        for attachments_item_data in _attachments or []:
            attachments_item = SlackAttachment.from_dict(attachments_item_data)

            attachments.append(attachments_item)

        command_response = cls(
            response_type=response_type,
            text=text,
            username=username,
            icon_url=icon_url,
            goto_location=goto_location,
            attachments=attachments,
        )

        command_response.additional_properties = d
        return command_response

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
