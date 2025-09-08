from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.upload_session_type import UploadSessionType
from ..types import UNSET, Unset

T = TypeVar("T", bound="UploadSession")


@_attrs_define
class UploadSession:
    """an object containing information used to keep track of a file upload.

    Attributes:
        id (Union[Unset, str]): The unique identifier for the upload.
        type_ (Union[Unset, UploadSessionType]): The type of the upload.
        create_at (Union[Unset, int]): The time the upload was created in milliseconds.
        user_id (Union[Unset, str]): The ID of the user performing the upload.
        channel_id (Union[Unset, str]): The ID of the channel to upload to.
        filename (Union[Unset, str]): The name of the file to upload.
        file_size (Union[Unset, int]): The size of the file to upload in bytes.
        file_offset (Union[Unset, int]): The amount of data uploaded in bytes.
    """

    id: Union[Unset, str] = UNSET
    type_: Union[Unset, UploadSessionType] = UNSET
    create_at: Union[Unset, int] = UNSET
    user_id: Union[Unset, str] = UNSET
    channel_id: Union[Unset, str] = UNSET
    filename: Union[Unset, str] = UNSET
    file_size: Union[Unset, int] = UNSET
    file_offset: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        create_at = self.create_at

        user_id = self.user_id

        channel_id = self.channel_id

        filename = self.filename

        file_size = self.file_size

        file_offset = self.file_offset

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if type_ is not UNSET:
            field_dict["type"] = type_
        if create_at is not UNSET:
            field_dict["create_at"] = create_at
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if channel_id is not UNSET:
            field_dict["channel_id"] = channel_id
        if filename is not UNSET:
            field_dict["filename"] = filename
        if file_size is not UNSET:
            field_dict["file_size"] = file_size
        if file_offset is not UNSET:
            field_dict["file_offset"] = file_offset

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, UploadSessionType]
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = UploadSessionType(_type_)

        create_at = d.pop("create_at", UNSET)

        user_id = d.pop("user_id", UNSET)

        channel_id = d.pop("channel_id", UNSET)

        filename = d.pop("filename", UNSET)

        file_size = d.pop("file_size", UNSET)

        file_offset = d.pop("file_offset", UNSET)

        upload_session = cls(
            id=id,
            type_=type_,
            create_at=create_at,
            user_id=user_id,
            channel_id=channel_id,
            filename=filename,
            file_size=file_size,
            file_offset=file_offset,
        )

        upload_session.additional_properties = d
        return upload_session

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
