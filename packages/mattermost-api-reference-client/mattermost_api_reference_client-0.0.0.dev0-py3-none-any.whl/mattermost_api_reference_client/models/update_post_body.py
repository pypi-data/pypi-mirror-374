from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdatePostBody")


@_attrs_define
class UpdatePostBody:
    """
    Attributes:
        id (str): ID of the post to update
        is_pinned (Union[Unset, bool]): Set to `true` to pin the post to the channel it is in
        message (Union[Unset, str]): The message text of the post
        has_reactions (Union[Unset, bool]): Set to `true` if the post has reactions to it
        props (Union[Unset, str]): A general JSON property bag to attach to the post
    """

    id: str
    is_pinned: Union[Unset, bool] = UNSET
    message: Union[Unset, str] = UNSET
    has_reactions: Union[Unset, bool] = UNSET
    props: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        is_pinned = self.is_pinned

        message = self.message

        has_reactions = self.has_reactions

        props = self.props

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
            }
        )
        if is_pinned is not UNSET:
            field_dict["is_pinned"] = is_pinned
        if message is not UNSET:
            field_dict["message"] = message
        if has_reactions is not UNSET:
            field_dict["has_reactions"] = has_reactions
        if props is not UNSET:
            field_dict["props"] = props

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        is_pinned = d.pop("is_pinned", UNSET)

        message = d.pop("message", UNSET)

        has_reactions = d.pop("has_reactions", UNSET)

        props = d.pop("props", UNSET)

        update_post_body = cls(
            id=id,
            is_pinned=is_pinned,
            message=message,
            has_reactions=has_reactions,
            props=props,
        )

        update_post_body.additional_properties = d
        return update_post_body

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
