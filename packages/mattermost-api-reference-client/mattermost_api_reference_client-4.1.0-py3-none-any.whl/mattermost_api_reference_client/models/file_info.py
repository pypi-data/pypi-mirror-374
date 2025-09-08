from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="FileInfo")


@_attrs_define
class FileInfo:
    """
    Attributes:
        id (Union[Unset, str]): The unique identifier for this file
        user_id (Union[Unset, str]): The ID of the user that uploaded this file
        post_id (Union[Unset, str]): If this file is attached to a post, the ID of that post
        create_at (Union[Unset, int]): The time in milliseconds a file was created
        update_at (Union[Unset, int]): The time in milliseconds a file was last updated
        delete_at (Union[Unset, int]): The time in milliseconds a file was deleted
        name (Union[Unset, str]): The name of the file
        extension (Union[Unset, str]): The extension at the end of the file name
        size (Union[Unset, int]): The size of the file in bytes
        mime_type (Union[Unset, str]): The MIME type of the file
        width (Union[Unset, int]): If this file is an image, the width of the file
        height (Union[Unset, int]): If this file is an image, the height of the file
        has_preview_image (Union[Unset, bool]): If this file is an image, whether or not it has a preview-sized version
    """

    id: Union[Unset, str] = UNSET
    user_id: Union[Unset, str] = UNSET
    post_id: Union[Unset, str] = UNSET
    create_at: Union[Unset, int] = UNSET
    update_at: Union[Unset, int] = UNSET
    delete_at: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    extension: Union[Unset, str] = UNSET
    size: Union[Unset, int] = UNSET
    mime_type: Union[Unset, str] = UNSET
    width: Union[Unset, int] = UNSET
    height: Union[Unset, int] = UNSET
    has_preview_image: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        user_id = self.user_id

        post_id = self.post_id

        create_at = self.create_at

        update_at = self.update_at

        delete_at = self.delete_at

        name = self.name

        extension = self.extension

        size = self.size

        mime_type = self.mime_type

        width = self.width

        height = self.height

        has_preview_image = self.has_preview_image

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if post_id is not UNSET:
            field_dict["post_id"] = post_id
        if create_at is not UNSET:
            field_dict["create_at"] = create_at
        if update_at is not UNSET:
            field_dict["update_at"] = update_at
        if delete_at is not UNSET:
            field_dict["delete_at"] = delete_at
        if name is not UNSET:
            field_dict["name"] = name
        if extension is not UNSET:
            field_dict["extension"] = extension
        if size is not UNSET:
            field_dict["size"] = size
        if mime_type is not UNSET:
            field_dict["mime_type"] = mime_type
        if width is not UNSET:
            field_dict["width"] = width
        if height is not UNSET:
            field_dict["height"] = height
        if has_preview_image is not UNSET:
            field_dict["has_preview_image"] = has_preview_image

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        user_id = d.pop("user_id", UNSET)

        post_id = d.pop("post_id", UNSET)

        create_at = d.pop("create_at", UNSET)

        update_at = d.pop("update_at", UNSET)

        delete_at = d.pop("delete_at", UNSET)

        name = d.pop("name", UNSET)

        extension = d.pop("extension", UNSET)

        size = d.pop("size", UNSET)

        mime_type = d.pop("mime_type", UNSET)

        width = d.pop("width", UNSET)

        height = d.pop("height", UNSET)

        has_preview_image = d.pop("has_preview_image", UNSET)

        file_info = cls(
            id=id,
            user_id=user_id,
            post_id=post_id,
            create_at=create_at,
            update_at=update_at,
            delete_at=delete_at,
            name=name,
            extension=extension,
            size=size,
            mime_type=mime_type,
            width=width,
            height=height,
            has_preview_image=has_preview_image,
        )

        file_info.additional_properties = d
        return file_info

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
