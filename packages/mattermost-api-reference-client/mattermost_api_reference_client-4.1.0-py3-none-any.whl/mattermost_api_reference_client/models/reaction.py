from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Reaction")


@_attrs_define
class Reaction:
    """
    Attributes:
        user_id (Union[Unset, str]): The ID of the user that made this reaction
        post_id (Union[Unset, str]): The ID of the post to which this reaction was made
        emoji_name (Union[Unset, str]): The name of the emoji that was used for this reaction
        create_at (Union[Unset, int]): The time in milliseconds this reaction was made
    """

    user_id: Union[Unset, str] = UNSET
    post_id: Union[Unset, str] = UNSET
    emoji_name: Union[Unset, str] = UNSET
    create_at: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_id = self.user_id

        post_id = self.post_id

        emoji_name = self.emoji_name

        create_at = self.create_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if post_id is not UNSET:
            field_dict["post_id"] = post_id
        if emoji_name is not UNSET:
            field_dict["emoji_name"] = emoji_name
        if create_at is not UNSET:
            field_dict["create_at"] = create_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        user_id = d.pop("user_id", UNSET)

        post_id = d.pop("post_id", UNSET)

        emoji_name = d.pop("emoji_name", UNSET)

        create_at = d.pop("create_at", UNSET)

        reaction = cls(
            user_id=user_id,
            post_id=post_id,
            emoji_name=emoji_name,
            create_at=create_at,
        )

        reaction.additional_properties = d
        return reaction

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
