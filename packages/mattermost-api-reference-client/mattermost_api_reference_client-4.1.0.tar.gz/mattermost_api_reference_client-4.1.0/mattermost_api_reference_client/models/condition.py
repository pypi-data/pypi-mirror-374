from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Condition")


@_attrs_define
class Condition:
    """
    Attributes:
        attribute (Union[Unset, str]): The attribute name.
        operator (Union[Unset, str]): The operator of a single condition.
        value (Union[Unset, str]): The value.
        value_type (Union[Unset, str]): The value type.
    """

    attribute: Union[Unset, str] = UNSET
    operator: Union[Unset, str] = UNSET
    value: Union[Unset, str] = UNSET
    value_type: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        attribute = self.attribute

        operator = self.operator

        value = self.value

        value_type = self.value_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if attribute is not UNSET:
            field_dict["attribute"] = attribute
        if operator is not UNSET:
            field_dict["operator"] = operator
        if value is not UNSET:
            field_dict["value"] = value
        if value_type is not UNSET:
            field_dict["value_type"] = value_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        attribute = d.pop("attribute", UNSET)

        operator = d.pop("operator", UNSET)

        value = d.pop("value", UNSET)

        value_type = d.pop("value_type", UNSET)

        condition = cls(
            attribute=attribute,
            operator=operator,
            value=value,
            value_type=value_type,
        )

        condition.additional_properties = d
        return condition

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
