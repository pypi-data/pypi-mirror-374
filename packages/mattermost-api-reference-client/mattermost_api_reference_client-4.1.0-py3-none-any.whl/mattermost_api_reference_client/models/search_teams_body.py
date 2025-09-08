from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchTeamsBody")


@_attrs_define
class SearchTeamsBody:
    """
    Attributes:
        term (Union[Unset, str]): The search term to match against the name or display name of teams
        page (Union[Unset, str]): The page number to return, if paginated. If this parameter is not present with the
            `per_page` parameter then the results will be returned un-paged.
        per_page (Union[Unset, str]): The number of entries to return per page, if paginated. If this parameter is not
            present with the `page` parameter then the results will be returned un-paged.
        allow_open_invite (Union[Unset, bool]): Filters results to teams where `allow_open_invite` is set to true or
            false, excludes group constrained channels if this filter option is passed.
            If this filter option is not passed then the query will remain unchanged.
            __Minimum server version__: 5.28
        group_constrained (Union[Unset, bool]): Filters results to teams where `group_constrained` is set to true or
            false, returns the union of results when used with `allow_open_invite`
            If the filter option is not passed then the query will remain unchanged.
            __Minimum server version__: 5.28
        exclude_policy_constrained (Union[Unset, bool]): If set to true, only teams which do not have a granular
            retention policy assigned to them will be returned. The `sysconsole_read_compliance_data_retention` permission
            is required to use this parameter.
            __Minimum server version__: 5.35
             Default: False.
    """

    term: Union[Unset, str] = UNSET
    page: Union[Unset, str] = UNSET
    per_page: Union[Unset, str] = UNSET
    allow_open_invite: Union[Unset, bool] = UNSET
    group_constrained: Union[Unset, bool] = UNSET
    exclude_policy_constrained: Union[Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        term = self.term

        page = self.page

        per_page = self.per_page

        allow_open_invite = self.allow_open_invite

        group_constrained = self.group_constrained

        exclude_policy_constrained = self.exclude_policy_constrained

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if term is not UNSET:
            field_dict["term"] = term
        if page is not UNSET:
            field_dict["page"] = page
        if per_page is not UNSET:
            field_dict["per_page"] = per_page
        if allow_open_invite is not UNSET:
            field_dict["allow_open_invite"] = allow_open_invite
        if group_constrained is not UNSET:
            field_dict["group_constrained"] = group_constrained
        if exclude_policy_constrained is not UNSET:
            field_dict["exclude_policy_constrained"] = exclude_policy_constrained

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        term = d.pop("term", UNSET)

        page = d.pop("page", UNSET)

        per_page = d.pop("per_page", UNSET)

        allow_open_invite = d.pop("allow_open_invite", UNSET)

        group_constrained = d.pop("group_constrained", UNSET)

        exclude_policy_constrained = d.pop("exclude_policy_constrained", UNSET)

        search_teams_body = cls(
            term=term,
            page=page,
            per_page=per_page,
            allow_open_invite=allow_open_invite,
            group_constrained=group_constrained,
            exclude_policy_constrained=exclude_policy_constrained,
        )

        search_teams_body.additional_properties = d
        return search_teams_body

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
