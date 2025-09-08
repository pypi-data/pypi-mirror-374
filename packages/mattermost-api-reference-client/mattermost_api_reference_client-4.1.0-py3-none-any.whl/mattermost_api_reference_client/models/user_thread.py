from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post import Post


T = TypeVar("T", bound="UserThread")


@_attrs_define
class UserThread:
    """a thread that user is following

    Attributes:
        id (Union[Unset, str]): ID of the post that is this thread's root
        reply_count (Union[Unset, int]): number of replies in this thread
        last_reply_at (Union[Unset, int]): timestamp of the last post to this thread
        last_viewed_at (Union[Unset, int]): timestamp of the last time the user viewed this thread
        participants (Union[Unset, list['Post']]): list of users participating in this thread. only includes IDs unless
            'extended' was set to 'true'
        post (Union[Unset, Post]):
    """

    id: Union[Unset, str] = UNSET
    reply_count: Union[Unset, int] = UNSET
    last_reply_at: Union[Unset, int] = UNSET
    last_viewed_at: Union[Unset, int] = UNSET
    participants: Union[Unset, list["Post"]] = UNSET
    post: Union[Unset, "Post"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        reply_count = self.reply_count

        last_reply_at = self.last_reply_at

        last_viewed_at = self.last_viewed_at

        participants: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.participants, Unset):
            participants = []
            for participants_item_data in self.participants:
                participants_item = participants_item_data.to_dict()
                participants.append(participants_item)

        post: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.post, Unset):
            post = self.post.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if reply_count is not UNSET:
            field_dict["reply_count"] = reply_count
        if last_reply_at is not UNSET:
            field_dict["last_reply_at"] = last_reply_at
        if last_viewed_at is not UNSET:
            field_dict["last_viewed_at"] = last_viewed_at
        if participants is not UNSET:
            field_dict["participants"] = participants
        if post is not UNSET:
            field_dict["post"] = post

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post import Post

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        reply_count = d.pop("reply_count", UNSET)

        last_reply_at = d.pop("last_reply_at", UNSET)

        last_viewed_at = d.pop("last_viewed_at", UNSET)

        participants = []
        _participants = d.pop("participants", UNSET)
        for participants_item_data in _participants or []:
            participants_item = Post.from_dict(participants_item_data)

            participants.append(participants_item)

        _post = d.pop("post", UNSET)
        post: Union[Unset, Post]
        if isinstance(_post, Unset):
            post = UNSET
        else:
            post = Post.from_dict(_post)

        user_thread = cls(
            id=id,
            reply_count=reply_count,
            last_reply_at=last_reply_at,
            last_viewed_at=last_viewed_at,
            participants=participants,
            post=post,
        )

        user_thread.additional_properties = d
        return user_thread

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
