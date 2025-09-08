from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Group")


@_attrs_define
class Group:
    """
    Attributes:
        id (Union[Unset, str]):
        name (Union[Unset, str]):
        display_name (Union[Unset, str]):
        description (Union[Unset, str]):
        source (Union[Unset, str]):
        remote_id (Union[Unset, str]):
        create_at (Union[Unset, int]):
        update_at (Union[Unset, int]):
        delete_at (Union[Unset, int]):
        has_syncables (Union[Unset, bool]):
    """

    id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    display_name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    source: Union[Unset, str] = UNSET
    remote_id: Union[Unset, str] = UNSET
    create_at: Union[Unset, int] = UNSET
    update_at: Union[Unset, int] = UNSET
    delete_at: Union[Unset, int] = UNSET
    has_syncables: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        display_name = self.display_name

        description = self.description

        source = self.source

        remote_id = self.remote_id

        create_at = self.create_at

        update_at = self.update_at

        delete_at = self.delete_at

        has_syncables = self.has_syncables

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if description is not UNSET:
            field_dict["description"] = description
        if source is not UNSET:
            field_dict["source"] = source
        if remote_id is not UNSET:
            field_dict["remote_id"] = remote_id
        if create_at is not UNSET:
            field_dict["create_at"] = create_at
        if update_at is not UNSET:
            field_dict["update_at"] = update_at
        if delete_at is not UNSET:
            field_dict["delete_at"] = delete_at
        if has_syncables is not UNSET:
            field_dict["has_syncables"] = has_syncables

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        display_name = d.pop("display_name", UNSET)

        description = d.pop("description", UNSET)

        source = d.pop("source", UNSET)

        remote_id = d.pop("remote_id", UNSET)

        create_at = d.pop("create_at", UNSET)

        update_at = d.pop("update_at", UNSET)

        delete_at = d.pop("delete_at", UNSET)

        has_syncables = d.pop("has_syncables", UNSET)

        group = cls(
            id=id,
            name=name,
            display_name=display_name,
            description=description,
            source=source,
            remote_id=remote_id,
            create_at=create_at,
            update_at=update_at,
            delete_at=delete_at,
            has_syncables=has_syncables,
        )

        group.additional_properties = d
        return group

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
