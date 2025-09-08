from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post_metadata import PostMetadata
    from ..models.post_props import PostProps


T = TypeVar("T", bound="Post")


@_attrs_define
class Post:
    """
    Attributes:
        id (Union[Unset, str]):
        create_at (Union[Unset, int]): The time in milliseconds a post was created
        update_at (Union[Unset, int]): The time in milliseconds a post was last updated
        delete_at (Union[Unset, int]): The time in milliseconds a post was deleted
        edit_at (Union[Unset, int]):
        user_id (Union[Unset, str]):
        channel_id (Union[Unset, str]):
        root_id (Union[Unset, str]):
        original_id (Union[Unset, str]):
        message (Union[Unset, str]):
        type_ (Union[Unset, str]):
        props (Union[Unset, PostProps]):
        hashtag (Union[Unset, str]):
        file_ids (Union[Unset, list[str]]):
        pending_post_id (Union[Unset, str]):
        metadata (Union[Unset, PostMetadata]): Additional information used to display a post.
    """

    id: Union[Unset, str] = UNSET
    create_at: Union[Unset, int] = UNSET
    update_at: Union[Unset, int] = UNSET
    delete_at: Union[Unset, int] = UNSET
    edit_at: Union[Unset, int] = UNSET
    user_id: Union[Unset, str] = UNSET
    channel_id: Union[Unset, str] = UNSET
    root_id: Union[Unset, str] = UNSET
    original_id: Union[Unset, str] = UNSET
    message: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    props: Union[Unset, "PostProps"] = UNSET
    hashtag: Union[Unset, str] = UNSET
    file_ids: Union[Unset, list[str]] = UNSET
    pending_post_id: Union[Unset, str] = UNSET
    metadata: Union[Unset, "PostMetadata"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        create_at = self.create_at

        update_at = self.update_at

        delete_at = self.delete_at

        edit_at = self.edit_at

        user_id = self.user_id

        channel_id = self.channel_id

        root_id = self.root_id

        original_id = self.original_id

        message = self.message

        type_ = self.type_

        props: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.props, Unset):
            props = self.props.to_dict()

        hashtag = self.hashtag

        file_ids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.file_ids, Unset):
            file_ids = self.file_ids

        pending_post_id = self.pending_post_id

        metadata: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

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
        if edit_at is not UNSET:
            field_dict["edit_at"] = edit_at
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if channel_id is not UNSET:
            field_dict["channel_id"] = channel_id
        if root_id is not UNSET:
            field_dict["root_id"] = root_id
        if original_id is not UNSET:
            field_dict["original_id"] = original_id
        if message is not UNSET:
            field_dict["message"] = message
        if type_ is not UNSET:
            field_dict["type"] = type_
        if props is not UNSET:
            field_dict["props"] = props
        if hashtag is not UNSET:
            field_dict["hashtag"] = hashtag
        if file_ids is not UNSET:
            field_dict["file_ids"] = file_ids
        if pending_post_id is not UNSET:
            field_dict["pending_post_id"] = pending_post_id
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_metadata import PostMetadata
        from ..models.post_props import PostProps

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        create_at = d.pop("create_at", UNSET)

        update_at = d.pop("update_at", UNSET)

        delete_at = d.pop("delete_at", UNSET)

        edit_at = d.pop("edit_at", UNSET)

        user_id = d.pop("user_id", UNSET)

        channel_id = d.pop("channel_id", UNSET)

        root_id = d.pop("root_id", UNSET)

        original_id = d.pop("original_id", UNSET)

        message = d.pop("message", UNSET)

        type_ = d.pop("type", UNSET)

        _props = d.pop("props", UNSET)
        props: Union[Unset, PostProps]
        if isinstance(_props, Unset):
            props = UNSET
        else:
            props = PostProps.from_dict(_props)

        hashtag = d.pop("hashtag", UNSET)

        file_ids = cast(list[str], d.pop("file_ids", UNSET))

        pending_post_id = d.pop("pending_post_id", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, PostMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = PostMetadata.from_dict(_metadata)

        post = cls(
            id=id,
            create_at=create_at,
            update_at=update_at,
            delete_at=delete_at,
            edit_at=edit_at,
            user_id=user_id,
            channel_id=channel_id,
            root_id=root_id,
            original_id=original_id,
            message=message,
            type_=type_,
            props=props,
            hashtag=hashtag,
            file_ids=file_ids,
            pending_post_id=pending_post_id,
            metadata=metadata,
        )

        post.additional_properties = d
        return post

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
