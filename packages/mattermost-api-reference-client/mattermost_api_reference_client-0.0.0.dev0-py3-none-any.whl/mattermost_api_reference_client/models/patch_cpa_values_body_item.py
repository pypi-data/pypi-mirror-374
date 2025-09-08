from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PatchCPAValuesBodyItem")


@_attrs_define
class PatchCPAValuesBodyItem:
    """
    Attributes:
        id (Union[Unset, str]):
        value (Union[Unset, list[str], str]):
    """

    id: Union[Unset, str] = UNSET
    value: Union[Unset, list[str], str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        value: Union[Unset, list[str], str]
        if isinstance(self.value, Unset):
            value = UNSET
        elif isinstance(self.value, list):
            value = self.value

        else:
            value = self.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        def _parse_value(data: object) -> Union[Unset, list[str], str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                value_type_1 = cast(list[str], data)

                return value_type_1
            except:  # noqa: E722
                pass
            return cast(Union[Unset, list[str], str], data)

        value = _parse_value(d.pop("value", UNSET))

        patch_cpa_values_body_item = cls(
            id=id,
            value=value,
        )

        patch_cpa_values_body_item.additional_properties = d
        return patch_cpa_values_body_item

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
