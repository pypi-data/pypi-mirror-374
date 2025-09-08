from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreatePlaybookRunFromPostBody")


@_attrs_define
class CreatePlaybookRunFromPostBody:
    """
    Attributes:
        name (str): The name of the playbook run. Example: Server down in EU cluster.
        owner_user_id (str): The identifier of the user who is commanding the playbook run. Example:
            bqnbdf8uc0a8yz4i39qrpgkvtg.
        team_id (str): The identifier of the team where the playbook run's channel is in. Example:
            61ji2mpflefup3cnuif80r5rde.
        playbook_id (str): The identifier of the playbook with from which this playbook run was created. Example:
            0y4a0ntte97cxvfont8y84wa7x.
        description (Union[Unset, str]): The description of the playbook run. Example: There is one server in the EU
            cluster that is not responding since April 12..
        post_id (Union[Unset, str]): If the playbook run was created from a post, this field contains the identifier of
            such post. If not, this field is empty. Example: b2ntfcrl4ujivl456ab4b3aago.
    """

    name: str
    owner_user_id: str
    team_id: str
    playbook_id: str
    description: Union[Unset, str] = UNSET
    post_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        owner_user_id = self.owner_user_id

        team_id = self.team_id

        playbook_id = self.playbook_id

        description = self.description

        post_id = self.post_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "owner_user_id": owner_user_id,
                "team_id": team_id,
                "playbook_id": playbook_id,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if post_id is not UNSET:
            field_dict["post_id"] = post_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        owner_user_id = d.pop("owner_user_id")

        team_id = d.pop("team_id")

        playbook_id = d.pop("playbook_id")

        description = d.pop("description", UNSET)

        post_id = d.pop("post_id", UNSET)

        create_playbook_run_from_post_body = cls(
            name=name,
            owner_user_id=owner_user_id,
            team_id=team_id,
            playbook_id=playbook_id,
            description=description,
            post_id=post_id,
        )

        create_playbook_run_from_post_body.additional_properties = d
        return create_playbook_run_from_post_body

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
