from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.checklist import Checklist


T = TypeVar("T", bound="WebhookOnStatusUpdatePayload")


@_attrs_define
class WebhookOnStatusUpdatePayload:
    """
    Attributes:
        id (Union[Unset, str]): A unique, 26 characters long, alphanumeric identifier for the playbook run. Example:
            mx3xyzdojfgyfdx8sc8of1gdme.
        name (Union[Unset, str]): The name of the playbook run. Example: Server down in EU cluster.
        description (Union[Unset, str]): The description of the playbook run. Example: There is one server in the EU
            cluster that is not responding since April 12..
        is_active (Union[Unset, bool]): True if the playbook run is ongoing; false if the playbook run is ended.
        owner_user_id (Union[Unset, str]): The identifier of the user that is commanding the playbook run. Example:
            bqnbdf8uc0a8yz4i39qrpgkvtg.
        team_id (Union[Unset, str]): The identifier of the team where the playbook run's channel is in. Example:
            61ji2mpflefup3cnuif80r5rde.
        channel_id (Union[Unset, str]): The identifier of the playbook run's channel. Example:
            hwrmiyzj3kadcilh3ukfcnsbt6.
        create_at (Union[Unset, int]): The playbook run creation timestamp, formatted as the number of milliseconds
            since the Unix epoch. Example: 1606807976289.
        end_at (Union[Unset, int]): The playbook run finish timestamp, formatted as the number of milliseconds since the
            Unix epoch. It equals 0 if the playbook run is not finished.
        delete_at (Union[Unset, int]): The playbook run deletion timestamp, formatted as the number of milliseconds
            since the Unix epoch. It equals 0 if the playbook run is not deleted.
        active_stage (Union[Unset, int]): Zero-based index of the currently active stage. Example: 1.
        active_stage_title (Union[Unset, str]): The title of the currently active stage. Example: Triage issue.
        post_id (Union[Unset, str]): If the playbook run was created from a post, this field contains the identifier of
            such post. If not, this field is empty. Example: b2ntfcrl4ujivl456ab4b3aago.
        playbook_id (Union[Unset, str]): The identifier of the playbook with from which this playbook run was created.
            Example: 0y4a0ntte97cxvfont8y84wa7x.
        checklists (Union[Unset, list['Checklist']]):
        channel_url (Union[Unset, str]): Absolute URL to the playbook run's channel. Example:
            https://example.com/ad-1/channels/channel-name.
        details_url (Union[Unset, str]): Absolute URL to the playbook run's details. Example:
            https://example.com/ad-1/playbooks/runs/playbookRunID.
    """

    id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    is_active: Union[Unset, bool] = UNSET
    owner_user_id: Union[Unset, str] = UNSET
    team_id: Union[Unset, str] = UNSET
    channel_id: Union[Unset, str] = UNSET
    create_at: Union[Unset, int] = UNSET
    end_at: Union[Unset, int] = UNSET
    delete_at: Union[Unset, int] = UNSET
    active_stage: Union[Unset, int] = UNSET
    active_stage_title: Union[Unset, str] = UNSET
    post_id: Union[Unset, str] = UNSET
    playbook_id: Union[Unset, str] = UNSET
    checklists: Union[Unset, list["Checklist"]] = UNSET
    channel_url: Union[Unset, str] = UNSET
    details_url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        description = self.description

        is_active = self.is_active

        owner_user_id = self.owner_user_id

        team_id = self.team_id

        channel_id = self.channel_id

        create_at = self.create_at

        end_at = self.end_at

        delete_at = self.delete_at

        active_stage = self.active_stage

        active_stage_title = self.active_stage_title

        post_id = self.post_id

        playbook_id = self.playbook_id

        checklists: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.checklists, Unset):
            checklists = []
            for checklists_item_data in self.checklists:
                checklists_item = checklists_item_data.to_dict()
                checklists.append(checklists_item)

        channel_url = self.channel_url

        details_url = self.details_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if owner_user_id is not UNSET:
            field_dict["owner_user_id"] = owner_user_id
        if team_id is not UNSET:
            field_dict["team_id"] = team_id
        if channel_id is not UNSET:
            field_dict["channel_id"] = channel_id
        if create_at is not UNSET:
            field_dict["create_at"] = create_at
        if end_at is not UNSET:
            field_dict["end_at"] = end_at
        if delete_at is not UNSET:
            field_dict["delete_at"] = delete_at
        if active_stage is not UNSET:
            field_dict["active_stage"] = active_stage
        if active_stage_title is not UNSET:
            field_dict["active_stage_title"] = active_stage_title
        if post_id is not UNSET:
            field_dict["post_id"] = post_id
        if playbook_id is not UNSET:
            field_dict["playbook_id"] = playbook_id
        if checklists is not UNSET:
            field_dict["checklists"] = checklists
        if channel_url is not UNSET:
            field_dict["channel_url"] = channel_url
        if details_url is not UNSET:
            field_dict["details_url"] = details_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.checklist import Checklist

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        is_active = d.pop("is_active", UNSET)

        owner_user_id = d.pop("owner_user_id", UNSET)

        team_id = d.pop("team_id", UNSET)

        channel_id = d.pop("channel_id", UNSET)

        create_at = d.pop("create_at", UNSET)

        end_at = d.pop("end_at", UNSET)

        delete_at = d.pop("delete_at", UNSET)

        active_stage = d.pop("active_stage", UNSET)

        active_stage_title = d.pop("active_stage_title", UNSET)

        post_id = d.pop("post_id", UNSET)

        playbook_id = d.pop("playbook_id", UNSET)

        checklists = []
        _checklists = d.pop("checklists", UNSET)
        for checklists_item_data in _checklists or []:
            checklists_item = Checklist.from_dict(checklists_item_data)

            checklists.append(checklists_item)

        channel_url = d.pop("channel_url", UNSET)

        details_url = d.pop("details_url", UNSET)

        webhook_on_status_update_payload = cls(
            id=id,
            name=name,
            description=description,
            is_active=is_active,
            owner_user_id=owner_user_id,
            team_id=team_id,
            channel_id=channel_id,
            create_at=create_at,
            end_at=end_at,
            delete_at=delete_at,
            active_stage=active_stage,
            active_stage_title=active_stage_title,
            post_id=post_id,
            playbook_id=playbook_id,
            checklists=checklists,
            channel_url=channel_url,
            details_url=details_url,
        )

        webhook_on_status_update_payload.additional_properties = d
        return webhook_on_status_update_payload

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
