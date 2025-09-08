from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post_list_posts import PostListPosts


T = TypeVar("T", bound="PostList")


@_attrs_define
class PostList:
    """
    Attributes:
        order (Union[Unset, list[str]]):  Example: ['post_id1', 'post_id12'].
        posts (Union[Unset, PostListPosts]):
        next_post_id (Union[Unset, str]): The ID of next post. Not omitted when empty or not relevant.
        prev_post_id (Union[Unset, str]): The ID of previous post. Not omitted when empty or not relevant.
        has_next (Union[Unset, bool]): Whether there are more items after this page.
    """

    order: Union[Unset, list[str]] = UNSET
    posts: Union[Unset, "PostListPosts"] = UNSET
    next_post_id: Union[Unset, str] = UNSET
    prev_post_id: Union[Unset, str] = UNSET
    has_next: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        order: Union[Unset, list[str]] = UNSET
        if not isinstance(self.order, Unset):
            order = self.order

        posts: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.posts, Unset):
            posts = self.posts.to_dict()

        next_post_id = self.next_post_id

        prev_post_id = self.prev_post_id

        has_next = self.has_next

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if order is not UNSET:
            field_dict["order"] = order
        if posts is not UNSET:
            field_dict["posts"] = posts
        if next_post_id is not UNSET:
            field_dict["next_post_id"] = next_post_id
        if prev_post_id is not UNSET:
            field_dict["prev_post_id"] = prev_post_id
        if has_next is not UNSET:
            field_dict["has_next"] = has_next

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_list_posts import PostListPosts

        d = dict(src_dict)
        order = cast(list[str], d.pop("order", UNSET))

        _posts = d.pop("posts", UNSET)
        posts: Union[Unset, PostListPosts]
        if isinstance(_posts, Unset):
            posts = UNSET
        else:
            posts = PostListPosts.from_dict(_posts)

        next_post_id = d.pop("next_post_id", UNSET)

        prev_post_id = d.pop("prev_post_id", UNSET)

        has_next = d.pop("has_next", UNSET)

        post_list = cls(
            order=order,
            posts=posts,
            next_post_id=next_post_id,
            prev_post_id=prev_post_id,
            has_next=has_next,
        )

        post_list.additional_properties = d
        return post_list

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
