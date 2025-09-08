from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SharedChannelRemote")


@_attrs_define
class SharedChannelRemote:
    """
    Attributes:
        id (Union[Unset, str]): The id of the shared channel remote
        channel_id (Union[Unset, str]): The id of the channel
        creator_id (Union[Unset, str]): Id of the user that invited the remote to share the channel
        create_at (Union[Unset, int]): Time in milliseconds that the remote was invited to the channel
        update_at (Union[Unset, int]): Time in milliseconds that the shared channel remote record was last updated
        delete_at (Union[Unset, int]): Time in milliseconds that the shared chanenl remote record was deleted
        is_invite_accepted (Union[Unset, bool]): Indicates if the invite has been accepted by the remote
        is_invite_confirmed (Union[Unset, bool]): Indicates if the invite has been confirmed by the remote
        remote_id (Union[Unset, str]): Id of the remote cluster that the channel is shared with
        last_post_update_at (Union[Unset, int]): Time in milliseconds of the last post in the channel that was
            synchronized with the remote update_at
        last_post_id (Union[Unset, str]): Id of the last post in the channel that was synchronized with the remote
        last_post_create_at (Union[Unset, str]): Time in milliseconds of the last post in the channel that was
            synchronized with the remote create_at
        last_post_create_id (Union[Unset, str]):
    """

    id: Union[Unset, str] = UNSET
    channel_id: Union[Unset, str] = UNSET
    creator_id: Union[Unset, str] = UNSET
    create_at: Union[Unset, int] = UNSET
    update_at: Union[Unset, int] = UNSET
    delete_at: Union[Unset, int] = UNSET
    is_invite_accepted: Union[Unset, bool] = UNSET
    is_invite_confirmed: Union[Unset, bool] = UNSET
    remote_id: Union[Unset, str] = UNSET
    last_post_update_at: Union[Unset, int] = UNSET
    last_post_id: Union[Unset, str] = UNSET
    last_post_create_at: Union[Unset, str] = UNSET
    last_post_create_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        channel_id = self.channel_id

        creator_id = self.creator_id

        create_at = self.create_at

        update_at = self.update_at

        delete_at = self.delete_at

        is_invite_accepted = self.is_invite_accepted

        is_invite_confirmed = self.is_invite_confirmed

        remote_id = self.remote_id

        last_post_update_at = self.last_post_update_at

        last_post_id = self.last_post_id

        last_post_create_at = self.last_post_create_at

        last_post_create_id = self.last_post_create_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if channel_id is not UNSET:
            field_dict["channel_id"] = channel_id
        if creator_id is not UNSET:
            field_dict["creator_id"] = creator_id
        if create_at is not UNSET:
            field_dict["create_at"] = create_at
        if update_at is not UNSET:
            field_dict["update_at"] = update_at
        if delete_at is not UNSET:
            field_dict["delete_at"] = delete_at
        if is_invite_accepted is not UNSET:
            field_dict["is_invite_accepted"] = is_invite_accepted
        if is_invite_confirmed is not UNSET:
            field_dict["is_invite_confirmed"] = is_invite_confirmed
        if remote_id is not UNSET:
            field_dict["remote_id"] = remote_id
        if last_post_update_at is not UNSET:
            field_dict["last_post_update_at"] = last_post_update_at
        if last_post_id is not UNSET:
            field_dict["last_post_id"] = last_post_id
        if last_post_create_at is not UNSET:
            field_dict["last_post_create_at"] = last_post_create_at
        if last_post_create_id is not UNSET:
            field_dict["last_post_create_id"] = last_post_create_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        channel_id = d.pop("channel_id", UNSET)

        creator_id = d.pop("creator_id", UNSET)

        create_at = d.pop("create_at", UNSET)

        update_at = d.pop("update_at", UNSET)

        delete_at = d.pop("delete_at", UNSET)

        is_invite_accepted = d.pop("is_invite_accepted", UNSET)

        is_invite_confirmed = d.pop("is_invite_confirmed", UNSET)

        remote_id = d.pop("remote_id", UNSET)

        last_post_update_at = d.pop("last_post_update_at", UNSET)

        last_post_id = d.pop("last_post_id", UNSET)

        last_post_create_at = d.pop("last_post_create_at", UNSET)

        last_post_create_id = d.pop("last_post_create_id", UNSET)

        shared_channel_remote = cls(
            id=id,
            channel_id=channel_id,
            creator_id=creator_id,
            create_at=create_at,
            update_at=update_at,
            delete_at=delete_at,
            is_invite_accepted=is_invite_accepted,
            is_invite_confirmed=is_invite_confirmed,
            remote_id=remote_id,
            last_post_update_at=last_post_update_at,
            last_post_id=last_post_id,
            last_post_create_at=last_post_create_at,
            last_post_create_id=last_post_create_id,
        )

        shared_channel_remote.additional_properties = d
        return shared_channel_remote

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
