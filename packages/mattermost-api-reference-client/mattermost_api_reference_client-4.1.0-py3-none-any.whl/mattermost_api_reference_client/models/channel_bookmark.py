from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.channel_bookmark_type import ChannelBookmarkType
from ..types import UNSET, Unset

T = TypeVar("T", bound="ChannelBookmark")


@_attrs_define
class ChannelBookmark:
    """
    Attributes:
        id (Union[Unset, str]):
        create_at (Union[Unset, int]): The time in milliseconds a channel bookmark was created
        update_at (Union[Unset, int]): The time in milliseconds a channel bookmark was last updated
        delete_at (Union[Unset, int]): The time in milliseconds a channel bookmark was deleted
        channel_id (Union[Unset, str]):
        owner_id (Union[Unset, str]): The ID of the user that the channel bookmark belongs to
        file_id (Union[Unset, str]): The ID of the file associated with the channel bookmark
        display_name (Union[Unset, str]):
        sort_order (Union[Unset, int]): The order of the channel bookmark
        link_url (Union[Unset, str]): The URL associated with the channel bookmark
        image_url (Union[Unset, str]): The URL of the image associated with the channel bookmark
        emoji (Union[Unset, str]):
        type_ (Union[Unset, ChannelBookmarkType]):
        original_id (Union[Unset, str]): The ID of the original channel bookmark
        parent_id (Union[Unset, str]): The ID of the parent channel bookmark
    """

    id: Union[Unset, str] = UNSET
    create_at: Union[Unset, int] = UNSET
    update_at: Union[Unset, int] = UNSET
    delete_at: Union[Unset, int] = UNSET
    channel_id: Union[Unset, str] = UNSET
    owner_id: Union[Unset, str] = UNSET
    file_id: Union[Unset, str] = UNSET
    display_name: Union[Unset, str] = UNSET
    sort_order: Union[Unset, int] = UNSET
    link_url: Union[Unset, str] = UNSET
    image_url: Union[Unset, str] = UNSET
    emoji: Union[Unset, str] = UNSET
    type_: Union[Unset, ChannelBookmarkType] = UNSET
    original_id: Union[Unset, str] = UNSET
    parent_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        create_at = self.create_at

        update_at = self.update_at

        delete_at = self.delete_at

        channel_id = self.channel_id

        owner_id = self.owner_id

        file_id = self.file_id

        display_name = self.display_name

        sort_order = self.sort_order

        link_url = self.link_url

        image_url = self.image_url

        emoji = self.emoji

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        original_id = self.original_id

        parent_id = self.parent_id

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
        if owner_id is not UNSET:
            field_dict["owner_id"] = owner_id
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
        if original_id is not UNSET:
            field_dict["original_id"] = original_id
        if parent_id is not UNSET:
            field_dict["parent_id"] = parent_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        create_at = d.pop("create_at", UNSET)

        update_at = d.pop("update_at", UNSET)

        delete_at = d.pop("delete_at", UNSET)

        channel_id = d.pop("channel_id", UNSET)

        owner_id = d.pop("owner_id", UNSET)

        file_id = d.pop("file_id", UNSET)

        display_name = d.pop("display_name", UNSET)

        sort_order = d.pop("sort_order", UNSET)

        link_url = d.pop("link_url", UNSET)

        image_url = d.pop("image_url", UNSET)

        emoji = d.pop("emoji", UNSET)

        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, ChannelBookmarkType]
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = ChannelBookmarkType(_type_)

        original_id = d.pop("original_id", UNSET)

        parent_id = d.pop("parent_id", UNSET)

        channel_bookmark = cls(
            id=id,
            create_at=create_at,
            update_at=update_at,
            delete_at=delete_at,
            channel_id=channel_id,
            owner_id=owner_id,
            file_id=file_id,
            display_name=display_name,
            sort_order=sort_order,
            link_url=link_url,
            image_url=image_url,
            emoji=emoji,
            type_=type_,
            original_id=original_id,
            parent_id=parent_id,
        )

        channel_bookmark.additional_properties = d
        return channel_bookmark

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
