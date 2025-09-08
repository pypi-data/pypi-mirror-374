from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PropertyValue")


@_attrs_define
class PropertyValue:
    """
    Attributes:
        id (Union[Unset, str]):
        target_id (Union[Unset, str]):
        target_type (Union[Unset, str]):
        group_id (Union[Unset, str]):
        field_id (Union[Unset, str]):
        value (Union[Unset, str]):
        create_at (Union[Unset, int]):
        update_at (Union[Unset, int]):
        delete_at (Union[Unset, int]):
    """

    id: Union[Unset, str] = UNSET
    target_id: Union[Unset, str] = UNSET
    target_type: Union[Unset, str] = UNSET
    group_id: Union[Unset, str] = UNSET
    field_id: Union[Unset, str] = UNSET
    value: Union[Unset, str] = UNSET
    create_at: Union[Unset, int] = UNSET
    update_at: Union[Unset, int] = UNSET
    delete_at: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        target_id = self.target_id

        target_type = self.target_type

        group_id = self.group_id

        field_id = self.field_id

        value = self.value

        create_at = self.create_at

        update_at = self.update_at

        delete_at = self.delete_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if target_id is not UNSET:
            field_dict["target_id"] = target_id
        if target_type is not UNSET:
            field_dict["target_type"] = target_type
        if group_id is not UNSET:
            field_dict["group_id"] = group_id
        if field_id is not UNSET:
            field_dict["field_id"] = field_id
        if value is not UNSET:
            field_dict["value"] = value
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

        target_id = d.pop("target_id", UNSET)

        target_type = d.pop("target_type", UNSET)

        group_id = d.pop("group_id", UNSET)

        field_id = d.pop("field_id", UNSET)

        value = d.pop("value", UNSET)

        create_at = d.pop("create_at", UNSET)

        update_at = d.pop("update_at", UNSET)

        delete_at = d.pop("delete_at", UNSET)

        property_value = cls(
            id=id,
            target_id=target_id,
            target_type=target_type,
            group_id=group_id,
            field_id=field_id,
            value=value,
            create_at=create_at,
            update_at=update_at,
            delete_at=delete_at,
        )

        property_value.additional_properties = d
        return property_value

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
