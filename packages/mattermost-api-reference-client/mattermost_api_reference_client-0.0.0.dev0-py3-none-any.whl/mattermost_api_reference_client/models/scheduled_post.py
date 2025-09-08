from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post_metadata import PostMetadata
    from ..models.scheduled_post_props import ScheduledPostProps


T = TypeVar("T", bound="ScheduledPost")


@_attrs_define
class ScheduledPost:
    """
    Attributes:
        id (Union[Unset, str]):
        create_at (Union[Unset, int]): The time in milliseconds a scheduled post was created
        update_at (Union[Unset, int]): The time in milliseconds a scheduled post was last updated
        user_id (Union[Unset, str]):
        channel_id (Union[Unset, str]):
        root_id (Union[Unset, str]):
        message (Union[Unset, str]):
        props (Union[Unset, ScheduledPostProps]):
        file_ids (Union[Unset, list[str]]):
        scheduled_at (Union[Unset, int]): The time in milliseconds a scheduled post is scheduled to be sent at
        processed_at (Union[Unset, int]): The time in milliseconds a scheduled post was processed at
        error_code (Union[Unset, str]): Explains the error behind why a scheduled post could not have been sent
        metadata (Union[Unset, PostMetadata]): Additional information used to display a post.
    """

    id: Union[Unset, str] = UNSET
    create_at: Union[Unset, int] = UNSET
    update_at: Union[Unset, int] = UNSET
    user_id: Union[Unset, str] = UNSET
    channel_id: Union[Unset, str] = UNSET
    root_id: Union[Unset, str] = UNSET
    message: Union[Unset, str] = UNSET
    props: Union[Unset, "ScheduledPostProps"] = UNSET
    file_ids: Union[Unset, list[str]] = UNSET
    scheduled_at: Union[Unset, int] = UNSET
    processed_at: Union[Unset, int] = UNSET
    error_code: Union[Unset, str] = UNSET
    metadata: Union[Unset, "PostMetadata"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        create_at = self.create_at

        update_at = self.update_at

        user_id = self.user_id

        channel_id = self.channel_id

        root_id = self.root_id

        message = self.message

        props: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.props, Unset):
            props = self.props.to_dict()

        file_ids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.file_ids, Unset):
            file_ids = self.file_ids

        scheduled_at = self.scheduled_at

        processed_at = self.processed_at

        error_code = self.error_code

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
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if channel_id is not UNSET:
            field_dict["channel_id"] = channel_id
        if root_id is not UNSET:
            field_dict["root_id"] = root_id
        if message is not UNSET:
            field_dict["message"] = message
        if props is not UNSET:
            field_dict["props"] = props
        if file_ids is not UNSET:
            field_dict["file_ids"] = file_ids
        if scheduled_at is not UNSET:
            field_dict["scheduled_at"] = scheduled_at
        if processed_at is not UNSET:
            field_dict["processed_at"] = processed_at
        if error_code is not UNSET:
            field_dict["error_code"] = error_code
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_metadata import PostMetadata
        from ..models.scheduled_post_props import ScheduledPostProps

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        create_at = d.pop("create_at", UNSET)

        update_at = d.pop("update_at", UNSET)

        user_id = d.pop("user_id", UNSET)

        channel_id = d.pop("channel_id", UNSET)

        root_id = d.pop("root_id", UNSET)

        message = d.pop("message", UNSET)

        _props = d.pop("props", UNSET)
        props: Union[Unset, ScheduledPostProps]
        if isinstance(_props, Unset):
            props = UNSET
        else:
            props = ScheduledPostProps.from_dict(_props)

        file_ids = cast(list[str], d.pop("file_ids", UNSET))

        scheduled_at = d.pop("scheduled_at", UNSET)

        processed_at = d.pop("processed_at", UNSET)

        error_code = d.pop("error_code", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, PostMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = PostMetadata.from_dict(_metadata)

        scheduled_post = cls(
            id=id,
            create_at=create_at,
            update_at=update_at,
            user_id=user_id,
            channel_id=channel_id,
            root_id=root_id,
            message=message,
            props=props,
            file_ids=file_ids,
            scheduled_at=scheduled_at,
            processed_at=processed_at,
            error_code=error_code,
            metadata=metadata,
        )

        scheduled_post.additional_properties = d
        return scheduled_post

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
