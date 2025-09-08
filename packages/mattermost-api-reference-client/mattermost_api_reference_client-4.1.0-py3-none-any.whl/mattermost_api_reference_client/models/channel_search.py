from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ChannelSearch")


@_attrs_define
class ChannelSearch:
    """
    Attributes:
        term (Union[Unset, str]): The string to search in the channel name, display name, and purpose.
        team_ids (Union[Unset, list[str]]): Filters results to channels belonging to the given team ids.
        public (Union[Unset, bool]): Filters results to only return Public / Open channels.
        private (Union[Unset, bool]): Filters results to only return Private channels.
        deleted (Union[Unset, bool]): Filters results to only return deleted / archived channels.
        include_deleted (Union[Unset, bool]): Whether to include deleted channels in the search results.
    """

    term: Union[Unset, str] = UNSET
    team_ids: Union[Unset, list[str]] = UNSET
    public: Union[Unset, bool] = UNSET
    private: Union[Unset, bool] = UNSET
    deleted: Union[Unset, bool] = UNSET
    include_deleted: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        term = self.term

        team_ids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.team_ids, Unset):
            team_ids = self.team_ids

        public = self.public

        private = self.private

        deleted = self.deleted

        include_deleted = self.include_deleted

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if term is not UNSET:
            field_dict["term"] = term
        if team_ids is not UNSET:
            field_dict["team_ids"] = team_ids
        if public is not UNSET:
            field_dict["public"] = public
        if private is not UNSET:
            field_dict["private"] = private
        if deleted is not UNSET:
            field_dict["deleted"] = deleted
        if include_deleted is not UNSET:
            field_dict["include_deleted"] = include_deleted

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        term = d.pop("term", UNSET)

        team_ids = cast(list[str], d.pop("team_ids", UNSET))

        public = d.pop("public", UNSET)

        private = d.pop("private", UNSET)

        deleted = d.pop("deleted", UNSET)

        include_deleted = d.pop("include_deleted", UNSET)

        channel_search = cls(
            term=term,
            team_ids=team_ids,
            public=public,
            private=private,
            deleted=deleted,
            include_deleted=include_deleted,
        )

        channel_search.additional_properties = d
        return channel_search

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
