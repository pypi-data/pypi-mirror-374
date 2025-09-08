from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="QueryExpressionParams")


@_attrs_define
class QueryExpressionParams:
    """
    Attributes:
        expression (Union[Unset, str]): The policy expression to test.
        term (Union[Unset, str]): A search term to filter users against whom the expression is tested.
        limit (Union[Unset, int]): The maximum number of users to return.
        after (Union[Unset, str]): The ID of the user to start the test after (for pagination).
    """

    expression: Union[Unset, str] = UNSET
    term: Union[Unset, str] = UNSET
    limit: Union[Unset, int] = UNSET
    after: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        expression = self.expression

        term = self.term

        limit = self.limit

        after = self.after

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if expression is not UNSET:
            field_dict["expression"] = expression
        if term is not UNSET:
            field_dict["term"] = term
        if limit is not UNSET:
            field_dict["limit"] = limit
        if after is not UNSET:
            field_dict["after"] = after

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        expression = d.pop("expression", UNSET)

        term = d.pop("term", UNSET)

        limit = d.pop("limit", UNSET)

        after = d.pop("after", UNSET)

        query_expression_params = cls(
            expression=expression,
            term=term,
            limit=limit,
            after=after,
        )

        query_expression_params.additional_properties = d
        return query_expression_params

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
