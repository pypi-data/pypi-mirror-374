from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.slack_attachment_field import SlackAttachmentField


T = TypeVar("T", bound="SlackAttachment")


@_attrs_define
class SlackAttachment:
    """
    Attributes:
        id (Union[Unset, str]):
        fallback (Union[Unset, str]):
        color (Union[Unset, str]):
        pretext (Union[Unset, str]):
        author_name (Union[Unset, str]):
        author_link (Union[Unset, str]):
        author_icon (Union[Unset, str]):
        title (Union[Unset, str]):
        title_link (Union[Unset, str]):
        text (Union[Unset, str]):
        fields (Union[Unset, list['SlackAttachmentField']]):
        image_url (Union[Unset, str]):
        thumb_url (Union[Unset, str]):
        footer (Union[Unset, str]):
        footer_icon (Union[Unset, str]):
        timestamp (Union[Unset, str]): The timestamp of the slack attachment, either type of string or integer
    """

    id: Union[Unset, str] = UNSET
    fallback: Union[Unset, str] = UNSET
    color: Union[Unset, str] = UNSET
    pretext: Union[Unset, str] = UNSET
    author_name: Union[Unset, str] = UNSET
    author_link: Union[Unset, str] = UNSET
    author_icon: Union[Unset, str] = UNSET
    title: Union[Unset, str] = UNSET
    title_link: Union[Unset, str] = UNSET
    text: Union[Unset, str] = UNSET
    fields: Union[Unset, list["SlackAttachmentField"]] = UNSET
    image_url: Union[Unset, str] = UNSET
    thumb_url: Union[Unset, str] = UNSET
    footer: Union[Unset, str] = UNSET
    footer_icon: Union[Unset, str] = UNSET
    timestamp: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        fallback = self.fallback

        color = self.color

        pretext = self.pretext

        author_name = self.author_name

        author_link = self.author_link

        author_icon = self.author_icon

        title = self.title

        title_link = self.title_link

        text = self.text

        fields: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.fields, Unset):
            fields = []
            for fields_item_data in self.fields:
                fields_item = fields_item_data.to_dict()
                fields.append(fields_item)

        image_url = self.image_url

        thumb_url = self.thumb_url

        footer = self.footer

        footer_icon = self.footer_icon

        timestamp = self.timestamp

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["Id"] = id
        if fallback is not UNSET:
            field_dict["Fallback"] = fallback
        if color is not UNSET:
            field_dict["Color"] = color
        if pretext is not UNSET:
            field_dict["Pretext"] = pretext
        if author_name is not UNSET:
            field_dict["AuthorName"] = author_name
        if author_link is not UNSET:
            field_dict["AuthorLink"] = author_link
        if author_icon is not UNSET:
            field_dict["AuthorIcon"] = author_icon
        if title is not UNSET:
            field_dict["Title"] = title
        if title_link is not UNSET:
            field_dict["TitleLink"] = title_link
        if text is not UNSET:
            field_dict["Text"] = text
        if fields is not UNSET:
            field_dict["Fields"] = fields
        if image_url is not UNSET:
            field_dict["ImageURL"] = image_url
        if thumb_url is not UNSET:
            field_dict["ThumbURL"] = thumb_url
        if footer is not UNSET:
            field_dict["Footer"] = footer
        if footer_icon is not UNSET:
            field_dict["FooterIcon"] = footer_icon
        if timestamp is not UNSET:
            field_dict["Timestamp"] = timestamp

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.slack_attachment_field import SlackAttachmentField

        d = dict(src_dict)
        id = d.pop("Id", UNSET)

        fallback = d.pop("Fallback", UNSET)

        color = d.pop("Color", UNSET)

        pretext = d.pop("Pretext", UNSET)

        author_name = d.pop("AuthorName", UNSET)

        author_link = d.pop("AuthorLink", UNSET)

        author_icon = d.pop("AuthorIcon", UNSET)

        title = d.pop("Title", UNSET)

        title_link = d.pop("TitleLink", UNSET)

        text = d.pop("Text", UNSET)

        fields = []
        _fields = d.pop("Fields", UNSET)
        for fields_item_data in _fields or []:
            fields_item = SlackAttachmentField.from_dict(fields_item_data)

            fields.append(fields_item)

        image_url = d.pop("ImageURL", UNSET)

        thumb_url = d.pop("ThumbURL", UNSET)

        footer = d.pop("Footer", UNSET)

        footer_icon = d.pop("FooterIcon", UNSET)

        timestamp = d.pop("Timestamp", UNSET)

        slack_attachment = cls(
            id=id,
            fallback=fallback,
            color=color,
            pretext=pretext,
            author_name=author_name,
            author_link=author_link,
            author_icon=author_icon,
            title=title,
            title_link=title_link,
            text=text,
            fields=fields,
            image_url=image_url,
            thumb_url=thumb_url,
            footer=footer,
            footer_icon=footer_icon,
            timestamp=timestamp,
        )

        slack_attachment.additional_properties = d
        return slack_attachment

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
