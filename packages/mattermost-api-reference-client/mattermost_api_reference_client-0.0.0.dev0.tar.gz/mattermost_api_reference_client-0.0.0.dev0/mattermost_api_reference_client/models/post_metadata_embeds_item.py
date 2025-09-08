from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.post_metadata_embeds_item_type import PostMetadataEmbedsItemType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post_metadata_embeds_item_data import PostMetadataEmbedsItemData


T = TypeVar("T", bound="PostMetadataEmbedsItem")


@_attrs_define
class PostMetadataEmbedsItem:
    """
    Attributes:
        type_ (Union[Unset, PostMetadataEmbedsItemType]): The type of content that is embedded in this point.
        url (Union[Unset, str]): The URL of the embedded content, if one exists.
        data (Union[Unset, PostMetadataEmbedsItemData]): Any additional information about the embedded content. Only
            used at this time to store OpenGraph metadata.
            This field will be null for non-OpenGraph embeds.
    """

    type_: Union[Unset, PostMetadataEmbedsItemType] = UNSET
    url: Union[Unset, str] = UNSET
    data: Union[Unset, "PostMetadataEmbedsItemData"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        url = self.url

        data: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.data, Unset):
            data = self.data.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if type_ is not UNSET:
            field_dict["type"] = type_
        if url is not UNSET:
            field_dict["url"] = url
        if data is not UNSET:
            field_dict["data"] = data

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_metadata_embeds_item_data import PostMetadataEmbedsItemData

        d = dict(src_dict)
        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, PostMetadataEmbedsItemType]
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = PostMetadataEmbedsItemType(_type_)

        url = d.pop("url", UNSET)

        _data = d.pop("data", UNSET)
        data: Union[Unset, PostMetadataEmbedsItemData]
        if isinstance(_data, Unset):
            data = UNSET
        else:
            data = PostMetadataEmbedsItemData.from_dict(_data)

        post_metadata_embeds_item = cls(
            type_=type_,
            url=url,
            data=data,
        )

        post_metadata_embeds_item.additional_properties = d
        return post_metadata_embeds_item

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
