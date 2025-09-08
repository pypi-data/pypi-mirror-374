from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.property_field_attrs import PropertyFieldAttrs


T = TypeVar("T", bound="PropertyField")


@_attrs_define
class PropertyField:
    """
    Attributes:
        id (Union[Unset, str]):
        group_id (Union[Unset, str]):
        name (Union[Unset, str]):
        type_ (Union[Unset, str]):
        attrs (Union[Unset, PropertyFieldAttrs]):
        target_id (Union[Unset, str]):
        target_type (Union[Unset, str]):
        create_at (Union[Unset, int]):
        update_at (Union[Unset, int]):
        delete_at (Union[Unset, int]):
    """

    id: Union[Unset, str] = UNSET
    group_id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    attrs: Union[Unset, "PropertyFieldAttrs"] = UNSET
    target_id: Union[Unset, str] = UNSET
    target_type: Union[Unset, str] = UNSET
    create_at: Union[Unset, int] = UNSET
    update_at: Union[Unset, int] = UNSET
    delete_at: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        group_id = self.group_id

        name = self.name

        type_ = self.type_

        attrs: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.attrs, Unset):
            attrs = self.attrs.to_dict()

        target_id = self.target_id

        target_type = self.target_type

        create_at = self.create_at

        update_at = self.update_at

        delete_at = self.delete_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if group_id is not UNSET:
            field_dict["group_id"] = group_id
        if name is not UNSET:
            field_dict["name"] = name
        if type_ is not UNSET:
            field_dict["type"] = type_
        if attrs is not UNSET:
            field_dict["attrs"] = attrs
        if target_id is not UNSET:
            field_dict["target_id"] = target_id
        if target_type is not UNSET:
            field_dict["target_type"] = target_type
        if create_at is not UNSET:
            field_dict["create_at"] = create_at
        if update_at is not UNSET:
            field_dict["update_at"] = update_at
        if delete_at is not UNSET:
            field_dict["delete_at"] = delete_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.property_field_attrs import PropertyFieldAttrs

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        group_id = d.pop("group_id", UNSET)

        name = d.pop("name", UNSET)

        type_ = d.pop("type", UNSET)

        _attrs = d.pop("attrs", UNSET)
        attrs: Union[Unset, PropertyFieldAttrs]
        if isinstance(_attrs, Unset):
            attrs = UNSET
        else:
            attrs = PropertyFieldAttrs.from_dict(_attrs)

        target_id = d.pop("target_id", UNSET)

        target_type = d.pop("target_type", UNSET)

        create_at = d.pop("create_at", UNSET)

        update_at = d.pop("update_at", UNSET)

        delete_at = d.pop("delete_at", UNSET)

        property_field = cls(
            id=id,
            group_id=group_id,
            name=name,
            type_=type_,
            attrs=attrs,
            target_id=target_id,
            target_type=target_type,
            create_at=create_at,
            update_at=update_at,
            delete_at=delete_at,
        )

        property_field.additional_properties = d
        return property_field

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
