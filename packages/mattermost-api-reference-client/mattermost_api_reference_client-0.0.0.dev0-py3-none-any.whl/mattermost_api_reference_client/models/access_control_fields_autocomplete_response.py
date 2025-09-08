from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.access_control_fields_autocomplete_response_fields_item import (
        AccessControlFieldsAutocompleteResponseFieldsItem,
    )


T = TypeVar("T", bound="AccessControlFieldsAutocompleteResponse")


@_attrs_define
class AccessControlFieldsAutocompleteResponse:
    """
    Attributes:
        fields (Union[Unset, list['AccessControlFieldsAutocompleteResponseFieldsItem']]):
    """

    fields: Union[Unset, list["AccessControlFieldsAutocompleteResponseFieldsItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        fields: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.fields, Unset):
            fields = []
            for fields_item_data in self.fields:
                fields_item = fields_item_data.to_dict()
                fields.append(fields_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if fields is not UNSET:
            field_dict["fields"] = fields

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.access_control_fields_autocomplete_response_fields_item import (
            AccessControlFieldsAutocompleteResponseFieldsItem,
        )

        d = dict(src_dict)
        fields = []
        _fields = d.pop("fields", UNSET)
        for fields_item_data in _fields or []:
            fields_item = AccessControlFieldsAutocompleteResponseFieldsItem.from_dict(fields_item_data)

            fields.append(fields_item)

        access_control_fields_autocomplete_response = cls(
            fields=fields,
        )

        access_control_fields_autocomplete_response.additional_properties = d
        return access_control_fields_autocomplete_response

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
