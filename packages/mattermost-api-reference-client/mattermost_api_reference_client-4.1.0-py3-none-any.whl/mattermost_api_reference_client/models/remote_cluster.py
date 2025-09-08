from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RemoteCluster")


@_attrs_define
class RemoteCluster:
    """
    Attributes:
        remote_id (Union[Unset, str]):
        remote_team_id (Union[Unset, str]):
        name (Union[Unset, str]):
        display_name (Union[Unset, str]):
        site_url (Union[Unset, str]): URL of the remote cluster
        default_team_id (Union[Unset, str]): The team where channels from invites are created
        create_at (Union[Unset, int]): Time in milliseconds that the remote cluster was created
        delete_at (Union[Unset, int]): Time in milliseconds that the remote cluster record was deleted
        last_ping_at (Union[Unset, int]): Time in milliseconds when the last ping to the remote cluster was run
        token (Union[Unset, str]):
        remote_token (Union[Unset, str]):
        topics (Union[Unset, str]):
        creator_id (Union[Unset, str]):
        plugin_id (Union[Unset, str]):
        options (Union[Unset, int]): A bitmask with a set of option flags
    """

    remote_id: Union[Unset, str] = UNSET
    remote_team_id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    display_name: Union[Unset, str] = UNSET
    site_url: Union[Unset, str] = UNSET
    default_team_id: Union[Unset, str] = UNSET
    create_at: Union[Unset, int] = UNSET
    delete_at: Union[Unset, int] = UNSET
    last_ping_at: Union[Unset, int] = UNSET
    token: Union[Unset, str] = UNSET
    remote_token: Union[Unset, str] = UNSET
    topics: Union[Unset, str] = UNSET
    creator_id: Union[Unset, str] = UNSET
    plugin_id: Union[Unset, str] = UNSET
    options: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        remote_id = self.remote_id

        remote_team_id = self.remote_team_id

        name = self.name

        display_name = self.display_name

        site_url = self.site_url

        default_team_id = self.default_team_id

        create_at = self.create_at

        delete_at = self.delete_at

        last_ping_at = self.last_ping_at

        token = self.token

        remote_token = self.remote_token

        topics = self.topics

        creator_id = self.creator_id

        plugin_id = self.plugin_id

        options = self.options

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if remote_id is not UNSET:
            field_dict["remote_id"] = remote_id
        if remote_team_id is not UNSET:
            field_dict["remote_team_id"] = remote_team_id
        if name is not UNSET:
            field_dict["name"] = name
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if site_url is not UNSET:
            field_dict["site_url"] = site_url
        if default_team_id is not UNSET:
            field_dict["default_team_id"] = default_team_id
        if create_at is not UNSET:
            field_dict["create_at"] = create_at
        if delete_at is not UNSET:
            field_dict["delete_at"] = delete_at
        if last_ping_at is not UNSET:
            field_dict["last_ping_at"] = last_ping_at
        if token is not UNSET:
            field_dict["token"] = token
        if remote_token is not UNSET:
            field_dict["remote_token"] = remote_token
        if topics is not UNSET:
            field_dict["topics"] = topics
        if creator_id is not UNSET:
            field_dict["creator_id"] = creator_id
        if plugin_id is not UNSET:
            field_dict["plugin_id"] = plugin_id
        if options is not UNSET:
            field_dict["options"] = options

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        remote_id = d.pop("remote_id", UNSET)

        remote_team_id = d.pop("remote_team_id", UNSET)

        name = d.pop("name", UNSET)

        display_name = d.pop("display_name", UNSET)

        site_url = d.pop("site_url", UNSET)

        default_team_id = d.pop("default_team_id", UNSET)

        create_at = d.pop("create_at", UNSET)

        delete_at = d.pop("delete_at", UNSET)

        last_ping_at = d.pop("last_ping_at", UNSET)

        token = d.pop("token", UNSET)

        remote_token = d.pop("remote_token", UNSET)

        topics = d.pop("topics", UNSET)

        creator_id = d.pop("creator_id", UNSET)

        plugin_id = d.pop("plugin_id", UNSET)

        options = d.pop("options", UNSET)

        remote_cluster = cls(
            remote_id=remote_id,
            remote_team_id=remote_team_id,
            name=name,
            display_name=display_name,
            site_url=site_url,
            default_team_id=default_team_id,
            create_at=create_at,
            delete_at=delete_at,
            last_ping_at=last_ping_at,
            token=token,
            remote_token=remote_token,
            topics=topics,
            creator_id=creator_id,
            plugin_id=plugin_id,
            options=options,
        )

        remote_cluster.additional_properties = d
        return remote_cluster

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
