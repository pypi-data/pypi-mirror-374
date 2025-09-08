from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AutocompleteSuggestion")


@_attrs_define
class AutocompleteSuggestion:
    """
    Attributes:
        complete (Union[Unset, str]): Completed suggestion
        suggestion (Union[Unset, str]): Predicted text user might want to input
        hint (Union[Unset, str]): Hint about suggested input
        description (Union[Unset, str]): Description of the suggested command
        icon_data (Union[Unset, str]): Base64 encoded svg image
    """

    complete: Union[Unset, str] = UNSET
    suggestion: Union[Unset, str] = UNSET
    hint: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    icon_data: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        complete = self.complete

        suggestion = self.suggestion

        hint = self.hint

        description = self.description

        icon_data = self.icon_data

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if complete is not UNSET:
            field_dict["Complete"] = complete
        if suggestion is not UNSET:
            field_dict["Suggestion"] = suggestion
        if hint is not UNSET:
            field_dict["Hint"] = hint
        if description is not UNSET:
            field_dict["Description"] = description
        if icon_data is not UNSET:
            field_dict["IconData"] = icon_data

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        complete = d.pop("Complete", UNSET)

        suggestion = d.pop("Suggestion", UNSET)

        hint = d.pop("Hint", UNSET)

        description = d.pop("Description", UNSET)

        icon_data = d.pop("IconData", UNSET)

        autocomplete_suggestion = cls(
            complete=complete,
            suggestion=suggestion,
            hint=hint,
            description=description,
            icon_data=icon_data,
        )

        autocomplete_suggestion.additional_properties = d
        return autocomplete_suggestion

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
