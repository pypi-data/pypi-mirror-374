from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Emoji")


@_attrs_define
class Emoji:
    """
    Attributes:
        id (Union[Unset, str]): The ID of the emoji
        creator_id (Union[Unset, str]): The ID of the user that made the emoji
        name (Union[Unset, str]): The name of the emoji
        create_at (Union[Unset, int]): The time in milliseconds the emoji was made
        update_at (Union[Unset, int]): The time in milliseconds the emoji was last updated
        delete_at (Union[Unset, int]): The time in milliseconds the emoji was deleted
    """

    id: Union[Unset, str] = UNSET
    creator_id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    create_at: Union[Unset, int] = UNSET
    update_at: Union[Unset, int] = UNSET
    delete_at: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        creator_id = self.creator_id

        name = self.name

        create_at = self.create_at

        update_at = self.update_at

        delete_at = self.delete_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if creator_id is not UNSET:
            field_dict["creator_id"] = creator_id
        if name is not UNSET:
            field_dict["name"] = name
        if create_at is not UNSET:
            field_dict["create_at"] = create_at
        if update_at is not UNSET:
            field_dict["update_at"] = update_at
        if delete_at is not UNSET:
            field_dict["delete_at"] = delete_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        creator_id = d.pop("creator_id", UNSET)

        name = d.pop("name", UNSET)

        create_at = d.pop("create_at", UNSET)

        update_at = d.pop("update_at", UNSET)

        delete_at = d.pop("delete_at", UNSET)

        emoji = cls(
            id=id,
            creator_id=creator_id,
            name=name,
            create_at=create_at,
            update_at=update_at,
            delete_at=delete_at,
        )

        emoji.additional_properties = d
        return emoji

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
