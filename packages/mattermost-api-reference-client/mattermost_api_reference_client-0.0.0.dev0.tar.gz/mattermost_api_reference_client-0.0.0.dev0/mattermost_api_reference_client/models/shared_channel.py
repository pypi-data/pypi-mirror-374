from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SharedChannel")


@_attrs_define
class SharedChannel:
    """
    Attributes:
        id (Union[Unset, str]): Channel id of the shared channel
        team_id (Union[Unset, str]):
        home (Union[Unset, bool]): Is this the home cluster for the shared channel
        readonly (Union[Unset, bool]): Is this shared channel shared as read only
        name (Union[Unset, str]): Channel name as it is shared (may be different than original channel name)
        display_name (Union[Unset, str]): Channel display name as it appears locally
        purpose (Union[Unset, str]):
        header (Union[Unset, str]):
        creator_id (Union[Unset, str]): Id of the user that shared the channel
        create_at (Union[Unset, int]): Time in milliseconds that the channel was shared
        update_at (Union[Unset, int]): Time in milliseconds that the shared channel record was last updated
        remote_id (Union[Unset, str]): Id of the remote cluster where the shared channel is homed
    """

    id: Union[Unset, str] = UNSET
    team_id: Union[Unset, str] = UNSET
    home: Union[Unset, bool] = UNSET
    readonly: Union[Unset, bool] = UNSET
    name: Union[Unset, str] = UNSET
    display_name: Union[Unset, str] = UNSET
    purpose: Union[Unset, str] = UNSET
    header: Union[Unset, str] = UNSET
    creator_id: Union[Unset, str] = UNSET
    create_at: Union[Unset, int] = UNSET
    update_at: Union[Unset, int] = UNSET
    remote_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        team_id = self.team_id

        home = self.home

        readonly = self.readonly

        name = self.name

        display_name = self.display_name

        purpose = self.purpose

        header = self.header

        creator_id = self.creator_id

        create_at = self.create_at

        update_at = self.update_at

        remote_id = self.remote_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if team_id is not UNSET:
            field_dict["team_id"] = team_id
        if home is not UNSET:
            field_dict["home"] = home
        if readonly is not UNSET:
            field_dict["readonly"] = readonly
        if name is not UNSET:
            field_dict["name"] = name
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if purpose is not UNSET:
            field_dict["purpose"] = purpose
        if header is not UNSET:
            field_dict["header"] = header
        if creator_id is not UNSET:
            field_dict["creator_id"] = creator_id
        if create_at is not UNSET:
            field_dict["create_at"] = create_at
        if update_at is not UNSET:
            field_dict["update_at"] = update_at
        if remote_id is not UNSET:
            field_dict["remote_id"] = remote_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        team_id = d.pop("team_id", UNSET)

        home = d.pop("home", UNSET)

        readonly = d.pop("readonly", UNSET)

        name = d.pop("name", UNSET)

        display_name = d.pop("display_name", UNSET)

        purpose = d.pop("purpose", UNSET)

        header = d.pop("header", UNSET)

        creator_id = d.pop("creator_id", UNSET)

        create_at = d.pop("create_at", UNSET)

        update_at = d.pop("update_at", UNSET)

        remote_id = d.pop("remote_id", UNSET)

        shared_channel = cls(
            id=id,
            team_id=team_id,
            home=home,
            readonly=readonly,
            name=name,
            display_name=display_name,
            purpose=purpose,
            header=header,
            creator_id=creator_id,
            create_at=create_at,
            update_at=update_at,
            remote_id=remote_id,
        )

        shared_channel.additional_properties = d
        return shared_channel

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
