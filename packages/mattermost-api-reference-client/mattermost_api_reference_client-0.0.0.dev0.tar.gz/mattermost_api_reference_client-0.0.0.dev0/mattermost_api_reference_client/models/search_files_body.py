from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .. import types
from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchFilesBody")


@_attrs_define
class SearchFilesBody:
    """
    Attributes:
        terms (str): The search terms as inputed by the user. To search for files from a user include
            `from:someusername`, using a user's username. To search in a specific channel include `in:somechannel`, using
            the channel name (not the display name). To search for specific extensions include `ext:extension`.
        is_or_search (bool): Set to true if an Or search should be performed vs an And search.
        time_zone_offset (Union[Unset, int]): Offset from UTC of user timezone for date searches. Default: 0.
        include_deleted_channels (Union[Unset, bool]): Set to true if deleted channels should be included in the search.
            (archived channels)
        page (Union[Unset, int]): The page to select. (Only works with Elasticsearch) Default: 0.
        per_page (Union[Unset, int]): The number of posts per page. (Only works with Elasticsearch) Default: 60.
    """

    terms: str
    is_or_search: bool
    time_zone_offset: Union[Unset, int] = 0
    include_deleted_channels: Union[Unset, bool] = UNSET
    page: Union[Unset, int] = 0
    per_page: Union[Unset, int] = 60
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        terms = self.terms

        is_or_search = self.is_or_search

        time_zone_offset = self.time_zone_offset

        include_deleted_channels = self.include_deleted_channels

        page = self.page

        per_page = self.per_page

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "terms": terms,
                "is_or_search": is_or_search,
            }
        )
        if time_zone_offset is not UNSET:
            field_dict["time_zone_offset"] = time_zone_offset
        if include_deleted_channels is not UNSET:
            field_dict["include_deleted_channels"] = include_deleted_channels
        if page is not UNSET:
            field_dict["page"] = page
        if per_page is not UNSET:
            field_dict["per_page"] = per_page

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        files.append(("terms", (None, str(self.terms).encode(), "text/plain")))

        files.append(("is_or_search", (None, str(self.is_or_search).encode(), "text/plain")))

        if not isinstance(self.time_zone_offset, Unset):
            files.append(("time_zone_offset", (None, str(self.time_zone_offset).encode(), "text/plain")))

        if not isinstance(self.include_deleted_channels, Unset):
            files.append(
                ("include_deleted_channels", (None, str(self.include_deleted_channels).encode(), "text/plain"))
            )

        if not isinstance(self.page, Unset):
            files.append(("page", (None, str(self.page).encode(), "text/plain")))

        if not isinstance(self.per_page, Unset):
            files.append(("per_page", (None, str(self.per_page).encode(), "text/plain")))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        terms = d.pop("terms")

        is_or_search = d.pop("is_or_search")

        time_zone_offset = d.pop("time_zone_offset", UNSET)

        include_deleted_channels = d.pop("include_deleted_channels", UNSET)

        page = d.pop("page", UNSET)

        per_page = d.pop("per_page", UNSET)

        search_files_body = cls(
            terms=terms,
            is_or_search=is_or_search,
            time_zone_offset=time_zone_offset,
            include_deleted_channels=include_deleted_channels,
            page=page,
            per_page=per_page,
        )

        search_files_body.additional_properties = d
        return search_files_body

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
