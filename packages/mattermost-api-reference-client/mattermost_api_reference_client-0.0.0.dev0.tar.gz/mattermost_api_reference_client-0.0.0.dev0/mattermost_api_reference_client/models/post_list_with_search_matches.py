from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post_list_with_search_matches_matches import PostListWithSearchMatchesMatches
    from ..models.post_list_with_search_matches_posts import PostListWithSearchMatchesPosts


T = TypeVar("T", bound="PostListWithSearchMatches")


@_attrs_define
class PostListWithSearchMatches:
    """
    Attributes:
        order (Union[Unset, list[str]]):  Example: ['post_id1', 'post_id12'].
        posts (Union[Unset, PostListWithSearchMatchesPosts]):
        matches (Union[Unset, PostListWithSearchMatchesMatches]): A mapping of post IDs to a list of matched terms
            within the post. This field will only be populated on servers running version 5.1 or greater with Elasticsearch
            enabled. Example: {'post_id1': ['search match 1', 'search match 2']}.
    """

    order: Union[Unset, list[str]] = UNSET
    posts: Union[Unset, "PostListWithSearchMatchesPosts"] = UNSET
    matches: Union[Unset, "PostListWithSearchMatchesMatches"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        order: Union[Unset, list[str]] = UNSET
        if not isinstance(self.order, Unset):
            order = self.order

        posts: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.posts, Unset):
            posts = self.posts.to_dict()

        matches: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.matches, Unset):
            matches = self.matches.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if order is not UNSET:
            field_dict["order"] = order
        if posts is not UNSET:
            field_dict["posts"] = posts
        if matches is not UNSET:
            field_dict["matches"] = matches

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_list_with_search_matches_matches import PostListWithSearchMatchesMatches
        from ..models.post_list_with_search_matches_posts import PostListWithSearchMatchesPosts

        d = dict(src_dict)
        order = cast(list[str], d.pop("order", UNSET))

        _posts = d.pop("posts", UNSET)
        posts: Union[Unset, PostListWithSearchMatchesPosts]
        if isinstance(_posts, Unset):
            posts = UNSET
        else:
            posts = PostListWithSearchMatchesPosts.from_dict(_posts)

        _matches = d.pop("matches", UNSET)
        matches: Union[Unset, PostListWithSearchMatchesMatches]
        if isinstance(_matches, Unset):
            matches = UNSET
        else:
            matches = PostListWithSearchMatchesMatches.from_dict(_matches)

        post_list_with_search_matches = cls(
            order=order,
            posts=posts,
            matches=matches,
        )

        post_list_with_search_matches.additional_properties = d
        return post_list_with_search_matches

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
