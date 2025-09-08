from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchAllChannelsBody")


@_attrs_define
class SearchAllChannelsBody:
    """
    Attributes:
        term (str): The string to search in the channel name, display name, and purpose.
        not_associated_to_group (Union[Unset, str]): A group id to exclude channels that are associated to that group
            via GroupChannel records.
        exclude_default_channels (Union[Unset, bool]): Exclude default channels from the results by setting this
            parameter to true.
        team_ids (Union[Unset, list[str]]): Filters results to channels belonging to the given team ids

            __Minimum server version__: 5.26
        group_constrained (Union[Unset, bool]): Filters results to only return channels constrained to a group

            __Minimum server version__: 5.26
        exclude_group_constrained (Union[Unset, bool]): Filters results to exclude channels constrained to a group

            __Minimum server version__: 5.26
        public (Union[Unset, bool]): Filters results to only return Public / Open channels, can be used in conjunction
            with `private` to return both `public` and `private` channels

            __Minimum server version__: 5.26
        private (Union[Unset, bool]): Filters results to only return Private channels, can be used in conjunction with
            `public` to return both `private` and `public` channels

            __Minimum server version__: 5.26
        deleted (Union[Unset, bool]): Filters results to only return deleted / archived channels

            __Minimum server version__: 5.26
        page (Union[Unset, str]): The page number to return, if paginated. If this parameter is not present with the
            `per_page` parameter then the results will be returned un-paged.
        per_page (Union[Unset, str]): The number of entries to return per page, if paginated. If this parameter is not
            present with the `page` parameter then the results will be returned un-paged.
        exclude_policy_constrained (Union[Unset, bool]): If set to true, only channels which do not have a granular
            retention policy assigned to them will be returned. The `sysconsole_read_compliance_data_retention` permission
            is required to use this parameter.
            __Minimum server version__: 5.35
             Default: False.
        include_search_by_id (Union[Unset, bool]): If set to true, returns channels where given search 'term' matches
            channel ID.
            __Minimum server version__: 5.35
             Default: False.
        exclude_remote (Union[Unset, bool]): If set to true, only returns channels that are local to this server.
            __Minimum server version__: 10.2
             Default: False.
    """

    term: str
    not_associated_to_group: Union[Unset, str] = UNSET
    exclude_default_channels: Union[Unset, bool] = UNSET
    team_ids: Union[Unset, list[str]] = UNSET
    group_constrained: Union[Unset, bool] = UNSET
    exclude_group_constrained: Union[Unset, bool] = UNSET
    public: Union[Unset, bool] = UNSET
    private: Union[Unset, bool] = UNSET
    deleted: Union[Unset, bool] = UNSET
    page: Union[Unset, str] = UNSET
    per_page: Union[Unset, str] = UNSET
    exclude_policy_constrained: Union[Unset, bool] = False
    include_search_by_id: Union[Unset, bool] = False
    exclude_remote: Union[Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        term = self.term

        not_associated_to_group = self.not_associated_to_group

        exclude_default_channels = self.exclude_default_channels

        team_ids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.team_ids, Unset):
            team_ids = self.team_ids

        group_constrained = self.group_constrained

        exclude_group_constrained = self.exclude_group_constrained

        public = self.public

        private = self.private

        deleted = self.deleted

        page = self.page

        per_page = self.per_page

        exclude_policy_constrained = self.exclude_policy_constrained

        include_search_by_id = self.include_search_by_id

        exclude_remote = self.exclude_remote

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "term": term,
            }
        )
        if not_associated_to_group is not UNSET:
            field_dict["not_associated_to_group"] = not_associated_to_group
        if exclude_default_channels is not UNSET:
            field_dict["exclude_default_channels"] = exclude_default_channels
        if team_ids is not UNSET:
            field_dict["team_ids"] = team_ids
        if group_constrained is not UNSET:
            field_dict["group_constrained"] = group_constrained
        if exclude_group_constrained is not UNSET:
            field_dict["exclude_group_constrained"] = exclude_group_constrained
        if public is not UNSET:
            field_dict["public"] = public
        if private is not UNSET:
            field_dict["private"] = private
        if deleted is not UNSET:
            field_dict["deleted"] = deleted
        if page is not UNSET:
            field_dict["page"] = page
        if per_page is not UNSET:
            field_dict["per_page"] = per_page
        if exclude_policy_constrained is not UNSET:
            field_dict["exclude_policy_constrained"] = exclude_policy_constrained
        if include_search_by_id is not UNSET:
            field_dict["include_search_by_id"] = include_search_by_id
        if exclude_remote is not UNSET:
            field_dict["exclude_remote"] = exclude_remote

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        term = d.pop("term")

        not_associated_to_group = d.pop("not_associated_to_group", UNSET)

        exclude_default_channels = d.pop("exclude_default_channels", UNSET)

        team_ids = cast(list[str], d.pop("team_ids", UNSET))

        group_constrained = d.pop("group_constrained", UNSET)

        exclude_group_constrained = d.pop("exclude_group_constrained", UNSET)

        public = d.pop("public", UNSET)

        private = d.pop("private", UNSET)

        deleted = d.pop("deleted", UNSET)

        page = d.pop("page", UNSET)

        per_page = d.pop("per_page", UNSET)

        exclude_policy_constrained = d.pop("exclude_policy_constrained", UNSET)

        include_search_by_id = d.pop("include_search_by_id", UNSET)

        exclude_remote = d.pop("exclude_remote", UNSET)

        search_all_channels_body = cls(
            term=term,
            not_associated_to_group=not_associated_to_group,
            exclude_default_channels=exclude_default_channels,
            team_ids=team_ids,
            group_constrained=group_constrained,
            exclude_group_constrained=exclude_group_constrained,
            public=public,
            private=private,
            deleted=deleted,
            page=page,
            per_page=per_page,
            exclude_policy_constrained=exclude_policy_constrained,
            include_search_by_id=include_search_by_id,
            exclude_remote=exclude_remote,
        )

        search_all_channels_body.additional_properties = d
        return search_all_channels_body

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
