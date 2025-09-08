from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.create_channel_bookmark_body_type import CreateChannelBookmarkBodyType
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateChannelBookmarkBody")


@_attrs_define
class CreateChannelBookmarkBody:
    """
    Attributes:
        display_name (str): The name of the channel bookmark
        type_ (CreateChannelBookmarkBodyType): * `link` for channel bookmarks that reference a link. `link_url` is
            requied
            * `file` for channel bookmarks that reference a file. `file_id` is required
        file_id (Union[Unset, str]): The ID of the file associated with the channel bookmark. Required for bookmarks of
            type 'file'
        link_url (Union[Unset, str]): The URL associated with the channel bookmark. Required for bookmarks of type
            'link'
        image_url (Union[Unset, str]): The URL of the image associated with the channel bookmark. Optional, only applies
            for bookmarks of type 'link'
        emoji (Union[Unset, str]): The emoji of the channel bookmark
    """

    display_name: str
    type_: CreateChannelBookmarkBodyType
    file_id: Union[Unset, str] = UNSET
    link_url: Union[Unset, str] = UNSET
    image_url: Union[Unset, str] = UNSET
    emoji: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        display_name = self.display_name

        type_ = self.type_.value

        file_id = self.file_id

        link_url = self.link_url

        image_url = self.image_url

        emoji = self.emoji

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "display_name": display_name,
                "type": type_,
            }
        )
        if file_id is not UNSET:
            field_dict["file_id"] = file_id
        if link_url is not UNSET:
            field_dict["link_url"] = link_url
        if image_url is not UNSET:
            field_dict["image_url"] = image_url
        if emoji is not UNSET:
            field_dict["emoji"] = emoji

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        display_name = d.pop("display_name")

        type_ = CreateChannelBookmarkBodyType(d.pop("type"))

        file_id = d.pop("file_id", UNSET)

        link_url = d.pop("link_url", UNSET)

        image_url = d.pop("image_url", UNSET)

        emoji = d.pop("emoji", UNSET)

        create_channel_bookmark_body = cls(
            display_name=display_name,
            type_=type_,
            file_id=file_id,
            link_url=link_url,
            image_url=image_url,
            emoji=emoji,
        )

        create_channel_bookmark_body.additional_properties = d
        return create_channel_bookmark_body

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
