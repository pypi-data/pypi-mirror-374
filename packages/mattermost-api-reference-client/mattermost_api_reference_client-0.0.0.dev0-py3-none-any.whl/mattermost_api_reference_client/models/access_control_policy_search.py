from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AccessControlPolicySearch")


@_attrs_define
class AccessControlPolicySearch:
    """
    Attributes:
        term (Union[Unset, str]): The search term to match against policy names or display names.
        is_active (Union[Unset, bool]): Filter policies by active status.
        page (Union[Unset, int]): The page number to return.
        per_page (Union[Unset, int]): The number of policies to return per page.
    """

    term: Union[Unset, str] = UNSET
    is_active: Union[Unset, bool] = UNSET
    page: Union[Unset, int] = UNSET
    per_page: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        term = self.term

        is_active = self.is_active

        page = self.page

        per_page = self.per_page

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if term is not UNSET:
            field_dict["term"] = term
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if page is not UNSET:
            field_dict["page"] = page
        if per_page is not UNSET:
            field_dict["per_page"] = per_page

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        term = d.pop("term", UNSET)

        is_active = d.pop("is_active", UNSET)

        page = d.pop("page", UNSET)

        per_page = d.pop("per_page", UNSET)

        access_control_policy_search = cls(
            term=term,
            is_active=is_active,
            page=page,
            per_page=per_page,
        )

        access_control_policy_search.additional_properties = d
        return access_control_policy_search

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
