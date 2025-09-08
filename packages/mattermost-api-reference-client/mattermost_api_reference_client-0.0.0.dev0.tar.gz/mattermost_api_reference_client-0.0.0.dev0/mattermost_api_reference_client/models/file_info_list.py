from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.file_info_list_file_infos import FileInfoListFileInfos


T = TypeVar("T", bound="FileInfoList")


@_attrs_define
class FileInfoList:
    """
    Attributes:
        order (Union[Unset, list[str]]):  Example: ['file_info_id1', 'file_info_id2'].
        file_infos (Union[Unset, FileInfoListFileInfos]):
        next_file_id (Union[Unset, str]): The ID of next file info. Not omitted when empty or not relevant.
        prev_file_id (Union[Unset, str]): The ID of previous file info. Not omitted when empty or not relevant.
    """

    order: Union[Unset, list[str]] = UNSET
    file_infos: Union[Unset, "FileInfoListFileInfos"] = UNSET
    next_file_id: Union[Unset, str] = UNSET
    prev_file_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        order: Union[Unset, list[str]] = UNSET
        if not isinstance(self.order, Unset):
            order = self.order

        file_infos: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.file_infos, Unset):
            file_infos = self.file_infos.to_dict()

        next_file_id = self.next_file_id

        prev_file_id = self.prev_file_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if order is not UNSET:
            field_dict["order"] = order
        if file_infos is not UNSET:
            field_dict["file_infos"] = file_infos
        if next_file_id is not UNSET:
            field_dict["next_file_id"] = next_file_id
        if prev_file_id is not UNSET:
            field_dict["prev_file_id"] = prev_file_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.file_info_list_file_infos import FileInfoListFileInfos

        d = dict(src_dict)
        order = cast(list[str], d.pop("order", UNSET))

        _file_infos = d.pop("file_infos", UNSET)
        file_infos: Union[Unset, FileInfoListFileInfos]
        if isinstance(_file_infos, Unset):
            file_infos = UNSET
        else:
            file_infos = FileInfoListFileInfos.from_dict(_file_infos)

        next_file_id = d.pop("next_file_id", UNSET)

        prev_file_id = d.pop("prev_file_id", UNSET)

        file_info_list = cls(
            order=order,
            file_infos=file_infos,
            next_file_id=next_file_id,
            prev_file_id=prev_file_id,
        )

        file_info_list.additional_properties = d
        return file_info_list

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
