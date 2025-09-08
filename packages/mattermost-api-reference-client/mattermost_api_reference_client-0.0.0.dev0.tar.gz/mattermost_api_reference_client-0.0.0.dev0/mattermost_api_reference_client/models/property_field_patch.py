from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.property_field_patch_attrs import PropertyFieldPatchAttrs


T = TypeVar("T", bound="PropertyFieldPatch")


@_attrs_define
class PropertyFieldPatch:
    """
    Attributes:
        name (Union[Unset, str]):
        type_ (Union[Unset, str]):
        attrs (Union[Unset, PropertyFieldPatchAttrs]):
        target_id (Union[Unset, str]):
        target_type (Union[Unset, str]):
    """

    name: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    attrs: Union[Unset, "PropertyFieldPatchAttrs"] = UNSET
    target_id: Union[Unset, str] = UNSET
    target_type: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        type_ = self.type_

        attrs: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.attrs, Unset):
            attrs = self.attrs.to_dict()

        target_id = self.target_id

        target_type = self.target_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
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

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.property_field_patch_attrs import PropertyFieldPatchAttrs

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        type_ = d.pop("type", UNSET)

        _attrs = d.pop("attrs", UNSET)
        attrs: Union[Unset, PropertyFieldPatchAttrs]
        if isinstance(_attrs, Unset):
            attrs = UNSET
        else:
            attrs = PropertyFieldPatchAttrs.from_dict(_attrs)

        target_id = d.pop("target_id", UNSET)

        target_type = d.pop("target_type", UNSET)

        property_field_patch = cls(
            name=name,
            type_=type_,
            attrs=attrs,
            target_id=target_id,
            target_type=target_type,
        )

        property_field_patch.additional_properties = d
        return property_field_patch

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
