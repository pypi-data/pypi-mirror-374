from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_cpa_field_body_attrs import CreateCPAFieldBodyAttrs


T = TypeVar("T", bound="CreateCPAFieldBody")


@_attrs_define
class CreateCPAFieldBody:
    """
    Attributes:
        name (str):
        type_ (str):
        attrs (Union[Unset, CreateCPAFieldBodyAttrs]):
    """

    name: str
    type_: str
    attrs: Union[Unset, "CreateCPAFieldBodyAttrs"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        type_ = self.type_

        attrs: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.attrs, Unset):
            attrs = self.attrs.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "type": type_,
            }
        )
        if attrs is not UNSET:
            field_dict["attrs"] = attrs

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_cpa_field_body_attrs import CreateCPAFieldBodyAttrs

        d = dict(src_dict)
        name = d.pop("name")

        type_ = d.pop("type")

        _attrs = d.pop("attrs", UNSET)
        attrs: Union[Unset, CreateCPAFieldBodyAttrs]
        if isinstance(_attrs, Unset):
            attrs = UNSET
        else:
            attrs = CreateCPAFieldBodyAttrs.from_dict(_attrs)

        create_cpa_field_body = cls(
            name=name,
            type_=type_,
            attrs=attrs,
        )

        create_cpa_field_body.additional_properties = d
        return create_cpa_field_body

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
