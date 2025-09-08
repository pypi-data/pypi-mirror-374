from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.update_channel_bookmark_body_type import UpdateChannelBookmarkBodyType
from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateChannelBookmarkBody")


@_attrs_define
class UpdateChannelBookmarkBody:
    """
    Attributes:
        file_id (Union[Unset, str]): The ID of the file associated with the channel bookmark. Required for bookmarks of
            type 'file'
        display_name (Union[Unset, str]): The name of the channel bookmark
        sort_order (Union[Unset, int]): The order of the channel bookmark
        link_url (Union[Unset, str]): The URL associated with the channel bookmark. Required for type bookmarks of type
            'link'
        image_url (Union[Unset, str]): The URL of the image associated with the channel bookmark
        emoji (Union[Unset, str]): The emoji of the channel bookmark
        type_ (Union[Unset, UpdateChannelBookmarkBodyType]): * `link` for channel bookmarks that reference a link.
            `link_url` is requied
            * `file` for channel bookmarks that reference a file. `file_id` is required
    """

    file_id: Union[Unset, str] = UNSET
    display_name: Union[Unset, str] = UNSET
    sort_order: Union[Unset, int] = UNSET
    link_url: Union[Unset, str] = UNSET
    image_url: Union[Unset, str] = UNSET
    emoji: Union[Unset, str] = UNSET
    type_: Union[Unset, UpdateChannelBookmarkBodyType] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        file_id = self.file_id

        display_name = self.display_name

        sort_order = self.sort_order

        link_url = self.link_url

        image_url = self.image_url

        emoji = self.emoji

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if file_id is not UNSET:
            field_dict["file_id"] = file_id
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if sort_order is not UNSET:
            field_dict["sort_order"] = sort_order
        if link_url is not UNSET:
            field_dict["link_url"] = link_url
        if image_url is not UNSET:
            field_dict["image_url"] = image_url
        if emoji is not UNSET:
            field_dict["emoji"] = emoji
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        file_id = d.pop("file_id", UNSET)

        display_name = d.pop("display_name", UNSET)

        sort_order = d.pop("sort_order", UNSET)

        link_url = d.pop("link_url", UNSET)

        image_url = d.pop("image_url", UNSET)

        emoji = d.pop("emoji", UNSET)

        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, UpdateChannelBookmarkBodyType]
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = UpdateChannelBookmarkBodyType(_type_)

        update_channel_bookmark_body = cls(
            file_id=file_id,
            display_name=display_name,
            sort_order=sort_order,
            link_url=link_url,
            image_url=image_url,
            emoji=emoji,
            type_=type_,
        )

        update_channel_bookmark_body.additional_properties = d
        return update_channel_bookmark_body

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
