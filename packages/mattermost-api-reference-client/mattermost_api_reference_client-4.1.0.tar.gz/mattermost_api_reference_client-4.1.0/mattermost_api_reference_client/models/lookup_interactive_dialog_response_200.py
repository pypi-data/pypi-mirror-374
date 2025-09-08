from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.lookup_interactive_dialog_response_200_options_item import (
        LookupInteractiveDialogResponse200OptionsItem,
    )


T = TypeVar("T", bound="LookupInteractiveDialogResponse200")


@_attrs_define
class LookupInteractiveDialogResponse200:
    """
    Attributes:
        options (Union[Unset, list['LookupInteractiveDialogResponse200OptionsItem']]): List of options returned from the
            lookup
    """

    options: Union[Unset, list["LookupInteractiveDialogResponse200OptionsItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        options: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.options, Unset):
            options = []
            for options_item_data in self.options:
                options_item = options_item_data.to_dict()
                options.append(options_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if options is not UNSET:
            field_dict["options"] = options

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.lookup_interactive_dialog_response_200_options_item import (
            LookupInteractiveDialogResponse200OptionsItem,
        )

        d = dict(src_dict)
        options = []
        _options = d.pop("options", UNSET)
        for options_item_data in _options or []:
            options_item = LookupInteractiveDialogResponse200OptionsItem.from_dict(options_item_data)

            options.append(options_item)

        lookup_interactive_dialog_response_200 = cls(
            options=options,
        )

        lookup_interactive_dialog_response_200.additional_properties = d
        return lookup_interactive_dialog_response_200

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
