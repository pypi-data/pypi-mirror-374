from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ExpressionError")


@_attrs_define
class ExpressionError:
    """
    Attributes:
        message (Union[Unset, str]): The error message.
        field (Union[Unset, str]): The field related to the error, if applicable.
        line (Union[Unset, int]): The line number where the error occurred in the expression.
        column (Union[Unset, int]): The column number where the error occurred in the expression.
    """

    message: Union[Unset, str] = UNSET
    field: Union[Unset, str] = UNSET
    line: Union[Unset, int] = UNSET
    column: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        message = self.message

        field = self.field

        line = self.line

        column = self.column

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if message is not UNSET:
            field_dict["message"] = message
        if field is not UNSET:
            field_dict["field"] = field
        if line is not UNSET:
            field_dict["line"] = line
        if column is not UNSET:
            field_dict["column"] = column

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        message = d.pop("message", UNSET)

        field = d.pop("field", UNSET)

        line = d.pop("line", UNSET)

        column = d.pop("column", UNSET)

        expression_error = cls(
            message=message,
            field=field,
            line=line,
            column=column,
        )

        expression_error.additional_properties = d
        return expression_error

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
