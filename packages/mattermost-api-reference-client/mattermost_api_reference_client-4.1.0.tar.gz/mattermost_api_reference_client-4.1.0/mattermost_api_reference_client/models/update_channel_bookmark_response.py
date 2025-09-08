from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.channel_bookmark_with_file_info import ChannelBookmarkWithFileInfo


T = TypeVar("T", bound="UpdateChannelBookmarkResponse")


@_attrs_define
class UpdateChannelBookmarkResponse:
    """
    Attributes:
        updated (Union[Unset, ChannelBookmarkWithFileInfo]):
        deleted (Union[Unset, ChannelBookmarkWithFileInfo]):
    """

    updated: Union[Unset, "ChannelBookmarkWithFileInfo"] = UNSET
    deleted: Union[Unset, "ChannelBookmarkWithFileInfo"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        updated: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.updated, Unset):
            updated = self.updated.to_dict()

        deleted: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.deleted, Unset):
            deleted = self.deleted.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if updated is not UNSET:
            field_dict["updated"] = updated
        if deleted is not UNSET:
            field_dict["deleted"] = deleted

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.channel_bookmark_with_file_info import ChannelBookmarkWithFileInfo

        d = dict(src_dict)
        _updated = d.pop("updated", UNSET)
        updated: Union[Unset, ChannelBookmarkWithFileInfo]
        if isinstance(_updated, Unset):
            updated = UNSET
        else:
            updated = ChannelBookmarkWithFileInfo.from_dict(_updated)

        _deleted = d.pop("deleted", UNSET)
        deleted: Union[Unset, ChannelBookmarkWithFileInfo]
        if isinstance(_deleted, Unset):
            deleted = UNSET
        else:
            deleted = ChannelBookmarkWithFileInfo.from_dict(_deleted)

        update_channel_bookmark_response = cls(
            updated=updated,
            deleted=deleted,
        )

        update_channel_bookmark_response.additional_properties = d
        return update_channel_bookmark_response

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
