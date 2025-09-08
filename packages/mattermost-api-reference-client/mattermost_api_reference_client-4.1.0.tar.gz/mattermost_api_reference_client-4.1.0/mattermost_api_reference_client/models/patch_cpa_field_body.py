from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.patch_cpa_field_body_attrs import PatchCPAFieldBodyAttrs


T = TypeVar("T", bound="PatchCPAFieldBody")


@_attrs_define
class PatchCPAFieldBody:
    """
    Attributes:
        name (Union[Unset, str]):
        type_ (Union[Unset, str]):
        attrs (Union[Unset, PatchCPAFieldBodyAttrs]):
    """

    name: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    attrs: Union[Unset, "PatchCPAFieldBodyAttrs"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        type_ = self.type_

        attrs: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.attrs, Unset):
            attrs = self.attrs.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if type_ is not UNSET:
            field_dict["type"] = type_
        if attrs is not UNSET:
            field_dict["attrs"] = attrs

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.patch_cpa_field_body_attrs import PatchCPAFieldBodyAttrs

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        type_ = d.pop("type", UNSET)

        _attrs = d.pop("attrs", UNSET)
        attrs: Union[Unset, PatchCPAFieldBodyAttrs]
        if isinstance(_attrs, Unset):
            attrs = UNSET
        else:
            attrs = PatchCPAFieldBodyAttrs.from_dict(_attrs)

        patch_cpa_field_body = cls(
            name=name,
            type_=type_,
            attrs=attrs,
        )

        patch_cpa_field_body.additional_properties = d
        return patch_cpa_field_body

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
