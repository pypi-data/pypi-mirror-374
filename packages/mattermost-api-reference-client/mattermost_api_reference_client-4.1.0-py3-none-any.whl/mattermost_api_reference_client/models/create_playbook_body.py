from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_playbook_body_checklists_item import CreatePlaybookBodyChecklistsItem


T = TypeVar("T", bound="CreatePlaybookBody")


@_attrs_define
class CreatePlaybookBody:
    """
    Attributes:
        title (str): The title of the playbook. Example: Cloud PlaybookRuns.
        team_id (str): The identifier of the team where the playbook is in. Example: p03rbi6viyztysbqnkvcqyel2i.
        create_public_playbook_run (bool): A boolean indicating whether the playbook runs created from this playbook
            should be public or private. Example: True.
        checklists (list['CreatePlaybookBodyChecklistsItem']): The stages defined by this playbook.
        member_ids (list[str]): The identifiers of all the users that are members of this playbook. Example:
            ilh6s1j4yefbdhxhtlzt179i6m.
        description (Union[Unset, str]): The description of the playbook. Example: A playbook to follow when there is a
            playbook run regarding the availability of the cloud service..
        public (Union[Unset, bool]): A boolean indicating whether the playbook is licensed as public or private.
            Required 'true' for free tier. Example: True.
        broadcast_channel_ids (Union[Unset, list[str]]): The IDs of the channels where all the status updates will be
            broadcasted. The team of the broadcast channel must be the same as the playbook's team. Example:
            2zh7rpashwfwapwaqyslmhwbax.
        invited_user_ids (Union[Unset, list[str]]): A list with the IDs of the members to be automatically invited to
            the playbook run's channel as soon as the playbook run is created. Example: 01kidjn9iozv7bist427w4gkjo.
        invite_users_enabled (Union[Unset, bool]): Boolean that indicates whether the members declared in
            invited_user_ids will be automatically invited. Example: True.
        default_owner_id (Union[Unset, str]): User ID of the member that will be automatically assigned as owner as soon
            as the playbook run is created. If the member is not part of the playbook run's channel or is not included in
            the invited_user_ids list, they will be automatically invited to the channel. Example:
            9dtruav6d9ce3oqnc5pwhtqtfq.
        default_owner_enabled (Union[Unset, str]): Boolean that indicates whether the member declared in
            default_owner_id will be automatically assigned as owner. Example: True.
        announcement_channel_id (Union[Unset, str]): ID of the channel where the playbook run will be automatically
            announced as soon as the playbook run is created. Example: 8iofau5swv32l6qtk3vlxgobta.
        announcement_channel_enabled (Union[Unset, bool]): Boolean that indicates whether the playbook run creation will
            be announced in the channel declared in announcement_channel_id. Example: True.
        webhook_on_creation_url (Union[Unset, str]): An absolute URL where a POST request will be sent as soon as the
            playbook run is created. The allowed protocols are HTTP and HTTPS. Example: https://httpbin.org/post.
        webhook_on_creation_enabled (Union[Unset, bool]): Boolean that indicates whether the webhook declared in
            webhook_on_creation_url will be automatically sent. Example: True.
        webhook_on_status_update_url (Union[Unset, str]): An absolute URL where a POST request will be sent as soon as
            the playbook run's status is updated. The allowed protocols are HTTP and HTTPS. Example:
            https://httpbin.org/post.
        webhook_on_status_update_enabled (Union[Unset, bool]): Boolean that indicates whether the webhook declared in
            webhook_on_status_update_url will be automatically sent. Example: True.
    """

    title: str
    team_id: str
    create_public_playbook_run: bool
    checklists: list["CreatePlaybookBodyChecklistsItem"]
    member_ids: list[str]
    description: Union[Unset, str] = UNSET
    public: Union[Unset, bool] = UNSET
    broadcast_channel_ids: Union[Unset, list[str]] = UNSET
    invited_user_ids: Union[Unset, list[str]] = UNSET
    invite_users_enabled: Union[Unset, bool] = UNSET
    default_owner_id: Union[Unset, str] = UNSET
    default_owner_enabled: Union[Unset, str] = UNSET
    announcement_channel_id: Union[Unset, str] = UNSET
    announcement_channel_enabled: Union[Unset, bool] = UNSET
    webhook_on_creation_url: Union[Unset, str] = UNSET
    webhook_on_creation_enabled: Union[Unset, bool] = UNSET
    webhook_on_status_update_url: Union[Unset, str] = UNSET
    webhook_on_status_update_enabled: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        team_id = self.team_id

        create_public_playbook_run = self.create_public_playbook_run

        checklists = []
        for checklists_item_data in self.checklists:
            checklists_item = checklists_item_data.to_dict()
            checklists.append(checklists_item)

        member_ids = self.member_ids

        description = self.description

        public = self.public

        broadcast_channel_ids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.broadcast_channel_ids, Unset):
            broadcast_channel_ids = self.broadcast_channel_ids

        invited_user_ids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.invited_user_ids, Unset):
            invited_user_ids = self.invited_user_ids

        invite_users_enabled = self.invite_users_enabled

        default_owner_id = self.default_owner_id

        default_owner_enabled = self.default_owner_enabled

        announcement_channel_id = self.announcement_channel_id

        announcement_channel_enabled = self.announcement_channel_enabled

        webhook_on_creation_url = self.webhook_on_creation_url

        webhook_on_creation_enabled = self.webhook_on_creation_enabled

        webhook_on_status_update_url = self.webhook_on_status_update_url

        webhook_on_status_update_enabled = self.webhook_on_status_update_enabled

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "title": title,
                "team_id": team_id,
                "create_public_playbook_run": create_public_playbook_run,
                "checklists": checklists,
                "member_ids": member_ids,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if public is not UNSET:
            field_dict["public"] = public
        if broadcast_channel_ids is not UNSET:
            field_dict["broadcast_channel_ids"] = broadcast_channel_ids
        if invited_user_ids is not UNSET:
            field_dict["invited_user_ids"] = invited_user_ids
        if invite_users_enabled is not UNSET:
            field_dict["invite_users_enabled"] = invite_users_enabled
        if default_owner_id is not UNSET:
            field_dict["default_owner_id"] = default_owner_id
        if default_owner_enabled is not UNSET:
            field_dict["default_owner_enabled"] = default_owner_enabled
        if announcement_channel_id is not UNSET:
            field_dict["announcement_channel_id"] = announcement_channel_id
        if announcement_channel_enabled is not UNSET:
            field_dict["announcement_channel_enabled"] = announcement_channel_enabled
        if webhook_on_creation_url is not UNSET:
            field_dict["webhook_on_creation_url"] = webhook_on_creation_url
        if webhook_on_creation_enabled is not UNSET:
            field_dict["webhook_on_creation_enabled"] = webhook_on_creation_enabled
        if webhook_on_status_update_url is not UNSET:
            field_dict["webhook_on_status_update_url"] = webhook_on_status_update_url
        if webhook_on_status_update_enabled is not UNSET:
            field_dict["webhook_on_status_update_enabled"] = webhook_on_status_update_enabled

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_playbook_body_checklists_item import CreatePlaybookBodyChecklistsItem

        d = dict(src_dict)
        title = d.pop("title")

        team_id = d.pop("team_id")

        create_public_playbook_run = d.pop("create_public_playbook_run")

        checklists = []
        _checklists = d.pop("checklists")
        for checklists_item_data in _checklists:
            checklists_item = CreatePlaybookBodyChecklistsItem.from_dict(checklists_item_data)

            checklists.append(checklists_item)

        member_ids = cast(list[str], d.pop("member_ids"))

        description = d.pop("description", UNSET)

        public = d.pop("public", UNSET)

        broadcast_channel_ids = cast(list[str], d.pop("broadcast_channel_ids", UNSET))

        invited_user_ids = cast(list[str], d.pop("invited_user_ids", UNSET))

        invite_users_enabled = d.pop("invite_users_enabled", UNSET)

        default_owner_id = d.pop("default_owner_id", UNSET)

        default_owner_enabled = d.pop("default_owner_enabled", UNSET)

        announcement_channel_id = d.pop("announcement_channel_id", UNSET)

        announcement_channel_enabled = d.pop("announcement_channel_enabled", UNSET)

        webhook_on_creation_url = d.pop("webhook_on_creation_url", UNSET)

        webhook_on_creation_enabled = d.pop("webhook_on_creation_enabled", UNSET)

        webhook_on_status_update_url = d.pop("webhook_on_status_update_url", UNSET)

        webhook_on_status_update_enabled = d.pop("webhook_on_status_update_enabled", UNSET)

        create_playbook_body = cls(
            title=title,
            team_id=team_id,
            create_public_playbook_run=create_public_playbook_run,
            checklists=checklists,
            member_ids=member_ids,
            description=description,
            public=public,
            broadcast_channel_ids=broadcast_channel_ids,
            invited_user_ids=invited_user_ids,
            invite_users_enabled=invite_users_enabled,
            default_owner_id=default_owner_id,
            default_owner_enabled=default_owner_enabled,
            announcement_channel_id=announcement_channel_id,
            announcement_channel_enabled=announcement_channel_enabled,
            webhook_on_creation_url=webhook_on_creation_url,
            webhook_on_creation_enabled=webhook_on_creation_enabled,
            webhook_on_status_update_url=webhook_on_status_update_url,
            webhook_on_status_update_enabled=webhook_on_status_update_enabled,
        )

        create_playbook_body.additional_properties = d
        return create_playbook_body

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
