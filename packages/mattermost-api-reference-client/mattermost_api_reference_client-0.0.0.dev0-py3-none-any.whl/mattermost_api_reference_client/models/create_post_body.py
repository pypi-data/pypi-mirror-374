from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_post_body_metadata import CreatePostBodyMetadata
    from ..models.create_post_body_props import CreatePostBodyProps


T = TypeVar("T", bound="CreatePostBody")


@_attrs_define
class CreatePostBody:
    """
    Attributes:
        channel_id (str): The channel ID to post in
        message (str): The message contents, can be formatted with Markdown
        root_id (Union[Unset, str]): The post ID to comment on
        file_ids (Union[Unset, list[str]]): A list of file IDs to associate with the post. Note that posts are limited
            to 5 files maximum. Please use additional posts for more files.
        props (Union[Unset, CreatePostBodyProps]): A general JSON property bag to attach to the post
        metadata (Union[Unset, CreatePostBodyMetadata]): A JSON object to add post metadata, e.g the post's priority
    """

    channel_id: str
    message: str
    root_id: Union[Unset, str] = UNSET
    file_ids: Union[Unset, list[str]] = UNSET
    props: Union[Unset, "CreatePostBodyProps"] = UNSET
    metadata: Union[Unset, "CreatePostBodyMetadata"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        channel_id = self.channel_id

        message = self.message

        root_id = self.root_id

        file_ids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.file_ids, Unset):
            file_ids = self.file_ids

        props: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.props, Unset):
            props = self.props.to_dict()

        metadata: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "channel_id": channel_id,
                "message": message,
            }
        )
        if root_id is not UNSET:
            field_dict["root_id"] = root_id
        if file_ids is not UNSET:
            field_dict["file_ids"] = file_ids
        if props is not UNSET:
            field_dict["props"] = props
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_post_body_metadata import CreatePostBodyMetadata
        from ..models.create_post_body_props import CreatePostBodyProps

        d = dict(src_dict)
        channel_id = d.pop("channel_id")

        message = d.pop("message")

        root_id = d.pop("root_id", UNSET)

        file_ids = cast(list[str], d.pop("file_ids", UNSET))

        _props = d.pop("props", UNSET)
        props: Union[Unset, CreatePostBodyProps]
        if isinstance(_props, Unset):
            props = UNSET
        else:
            props = CreatePostBodyProps.from_dict(_props)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, CreatePostBodyMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = CreatePostBodyMetadata.from_dict(_metadata)

        create_post_body = cls(
            channel_id=channel_id,
            message=message,
            root_id=root_id,
            file_ids=file_ids,
            props=props,
            metadata=metadata,
        )

        create_post_body.additional_properties = d
        return create_post_body

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
